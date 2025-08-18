# Matrix Archiver Migration Guide

## Overview

All database migrations for the Matrix Archiver are performed **manually via the Supabase Dashboard** for safety and control.

## Before Any Migration

### 1. Create Backup
```bash
# Always create a backup before migrating
python3 create_backup.py
```

### 2. Stop Archiver
```bash
# Stop the archiver to prevent data changes during migration
sudo systemctl stop matrix-archiver
# Or kill the process if running manually
```

## Running Migrations

### Via Supabase Dashboard
1. Go to **Supabase Dashboard** → Your Project → **SQL Editor**
2. Click **"New Query"**
3. Copy-paste the migration SQL from the `migrations/` directory
4. **Review the SQL carefully**
5. Click **"Run"**
6. Verify the results using the verification queries included in the migration

### Migration Files
- `migrations/001_initial_schema.sql` - Initial database setup
- `migrations/002_enhance_schema.sql` - PostgreSQL version (reference only)
- `supabase_dashboard_migration.sql` - Dashboard-ready version of 002

## After Migration

### 1. Verify Success
Each migration includes verification queries at the end. Run them to confirm:
- All tables exist
- New columns added
- Data integrity preserved
- Indexes created

### 2. Update Application Code
Update the archiver code to use new table names and columns.

### 3. Restart Services
```bash
sudo systemctl start matrix-archiver
./scripts/status-matrix.sh
```

## Rollback

If something goes wrong:
1. Use the backup created before migration
2. Or use the rollback script: `migrations/002_enhance_schema_rollback.sql`

## Migration History

| Version | Description | Status |
|---------|-------------|--------|
| 001 | Initial schema setup | ✅ Applied |
| 002 | Schema enhancements, organizations | 🔄 Ready to apply |

## Best Practices

1. **Always backup first** - Use `create_backup.py`
2. **Stop the archiver** - Prevent concurrent changes
3. **Review SQL carefully** - Understand what each migration does
4. **Test in staging first** - If you have a staging environment
5. **Manual execution only** - Use Supabase Dashboard SQL Editor
6. **Verify afterwards** - Run the verification queries
7. **Keep backups** - Don't delete backup files immediately

## Files Structure

```
/home/matrix-ai/services/archiver/
├── create_backup.py              # Backup utility
├── supabase_dashboard_migration.sql  # Ready-to-run migration
├── migrations/
│   ├── 001_initial_schema.sql    # Initial setup
│   ├── 002_enhance_schema.sql    # PostgreSQL version (reference)
│   └── 002_enhance_schema_rollback.sql  # Rollback script
├── backups/                      # Backup files (timestamped)
└── MIGRATION_README.md          # This guide
```