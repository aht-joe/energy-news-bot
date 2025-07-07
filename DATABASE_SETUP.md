# Database Setup and Persistence

## Overview
This document explains how to configure database persistence for the Energy News Bot API across different deployment environments.

## Database Configuration

### Environment Variables
- `DATABASE_PATH`: Specify a custom path for the SQLite database file
- If not set, the system will try these paths in order:
  1. `/tmp/news.db` (may persist longer on some platforms)
  2. `./news.db` (current directory fallback)

### Render Deployment
On Render's free tier, persistent disks are not available. The system uses:
1. `/tmp/news.db` as the preferred path (may persist longer than app directory)
2. Automatic database seeding to restore essential data after restarts
3. Comprehensive logging to track database location and operations

### Local Development
For local development, you can set a custom database path:
```bash
export DATABASE_PATH="/path/to/your/database.db"
```

## Database Seeding
The system automatically seeds essential data when tables are empty:
- **Keywords**: 太陽光発電, CPPA, PPA, 系統用蓄電池
- **Companies**: Tesla, 出光興産, ENEOS

This ensures that even if the database is reset, core functionality remains available.

## Troubleshooting
1. Check application logs for database path information
2. Verify that `CREATE TABLE IF NOT EXISTS` preserves existing data
3. Monitor POST operations to ensure data is being stored correctly
4. Test data persistence across service restarts

## Testing Database Persistence
1. Add test data via POST endpoints
2. Restart the service
3. Verify data still exists via GET endpoints
4. Check logs for database initialization messages
