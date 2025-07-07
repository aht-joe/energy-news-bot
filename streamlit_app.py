import streamlit as st
import sqlite3
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from news_collector import NewsCollector
from news_processor import NewsProcessor
from teams_notifier import TeamsNotifier

conn = sqlite3.connect('news.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)''')

conn.commit()

try:
    config = Config.load_from_file("config.json")
except Exception as e:
    st.error(f"Error loading configuration: {e}")
    st.stop()

page = st.sidebar.selectbox("メニュー", ["記事追加", "キーワード管理", "企業管理", "記事一覧", "記事処理実行"])

if page == "記事追加":
    st.title("記事URLの追加")
    url = st.text_input("記事のURLを入力")
    if st.button("追加"):
        if url:
            c.execute("INSERT INTO articles (url) VALUES (?)", (url,))
            conn.commit()
            st.success("記事を追加しました")
        else:
            st.error("URLを入力してください")

elif page == "キーワード管理":
    st.title("キーワード管理")
    new_keyword = st.text_input("新しいキーワードを入力")
    if st.button("キーワード追加"):
        if new_keyword:
            c.execute("INSERT INTO keywords (word) VALUES (?)", (new_keyword,))
            conn.commit()
            st.success("キーワードを追加しました")
        else:
            st.error("キーワードを入力してください")
    st.write("登録済みキーワード：")
    for row in c.execute("SELECT word FROM keywords"):
        st.write("- ", row[0])

elif page == "企業管理":
    st.title("企業名管理")
    new_company = st.text_input("新しい企業名を入力")
    if st.button("企業追加"):
        if new_company:
            c.execute("INSERT INTO companies (name) VALUES (?)", (new_company,))
            conn.commit()
            st.success("企業名を追加しました")
        else:
            st.error("企業名を入力してください")
    st.write("登録済み企業名：")
    for row in c.execute("SELECT name FROM companies"):
        st.write("- ", row[0])

elif page == "記事一覧":
    st.title("登録済みの記事")
    for row in c.execute("SELECT url FROM articles"):
        st.write("🔗 ", row[0])

elif page == "記事処理実行":
    st.title("🚀 記事処理とTeams投稿")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        article_count = c.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        st.metric("登録記事数", article_count)
    with col2:
        keyword_count = c.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        st.metric("登録キーワード数", keyword_count)
    with col3:
        company_count = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        st.metric("登録企業数", company_count)
    
    st.markdown("---")
    
    if st.button("🚀 記事処理を開始", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("ニュース収集中...")
            progress_bar.progress(25)
            
            collector = NewsCollector(config)
            news_articles = collector.collect_news()
            
            st.success(f"✅ {len(news_articles)} 件の記事を収集しました")
            
            status_text.text("記事処理中...")
            progress_bar.progress(50)
            
            processor = NewsProcessor(config)
            processed_articles = processor.process_articles(news_articles)
            
            st.success(f"✅ {len(processed_articles)} 件の記事を処理しました")
            
            if processed_articles:
                status_text.text("Teams投稿中...")
                progress_bar.progress(75)
                
                notifier = TeamsNotifier(config)
                articles_to_post = processed_articles[:config.max_teams_posts]
                notifier.post_articles(articles_to_post)
                
                st.success(f"✅ {len(articles_to_post)} 件の記事をTeamsに投稿しました")
            else:
                st.info("関連度の高い記事が見つかりませんでした")
            
            status_text.text("データベース更新中...")
            progress_bar.progress(100)
            
            for article in news_articles:
                try:
                    c.execute("INSERT OR IGNORE INTO articles (url) VALUES (?)", (article.get('url', ''),))
                except:
                    pass
            conn.commit()
            
            status_text.text("処理完了!")
            st.balloons()
            
        except Exception as e:
            st.error(f"処理中にエラーが発生しました: {e}")
            st.exception(e)

conn.close()
