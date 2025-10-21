# SQLite to PostgreSQL Migration Guide

This guide provides step-by-step instructions for migrating your Django project from SQLite to PostgreSQL on Railway.

## 📋 Prerequisites

- Python virtual environment (`myenv`) activated
- Access to Railway PostgreSQL database
- SQLite database file (`db.sqlite3`) with existing data
- Windows PowerShell or Command Prompt

## 🗄️ Database Information

**Current Database:** SQLite (`db.sqlite3`)

**Target Database:** PostgreSQL on Railway
```
Host: tramway.proxy.rlwy.net
Port: 16433
Database: railway
```

---

## 🚀 Migration Steps

### Step 1: Create Environment File

Create a `.env` file in the project root (`myProject/.env`):

```env
# Django Settings Module
DJANGO_SETTINGS_MODULE=myProject.settings

# PostgreSQL Database URL (Railway)
DATABASE_URL=postgresql://postgres:YesuTOqseYfJqYDXmGpobsvnvXrZmJie@tramway.proxy.rlwy.net:16433/railway

# Copy your existing environment variables from settings.py here if needed
# CLOUDINARY_CLOUD_NAME=your_cloud_name
# CLOUDINARY_API_KEY=your_api_key
# CLOUDINARY_API_SECRET=your_api_secret
# RESEND_API_KEY=your_resend_api_key
```

**Important:** Make sure `.env` is in your `.gitignore` file to avoid committing credentials!

### Step 2: Install Dependencies

Activate your virtual environment and install the required packages:

```powershell
# Activate virtual environment
myenv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**What's installed:**
- `psycopg[binary]` - PostgreSQL adapter for Python
- `dj-database-url` - Database URL parser
- `python-dotenv` - Environment variable loader

### Step 3: Backup Current SQLite Database

Create a backup of your SQLite database before proceeding:

```powershell
# Run the backup script
python backup_sqlite.py
```

This creates a timestamped backup in `backups/db_backup_YYYYMMDD_HHMMSS.sqlite3`

### Step 4: Verify Database Configuration

Check that both databases are configured correctly:

```powershell
# This should show both 'default' (PostgreSQL) and 'sqlite' databases
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES.keys())"
```

Expected output:
```
dict_keys(['default', 'sqlite'])
```

### Step 5: Create PostgreSQL Schema

Run migrations on the PostgreSQL database to create all tables:

```powershell
python manage.py migrate
```

**What this does:**
- Connects to PostgreSQL (via DATABASE_URL)
- Creates all database tables
- Applies all migrations
- Sets up Django's system tables

**Expected output:** You should see all migrations being applied successfully.

### Step 6: Export Data from SQLite

Use the custom management command to export data from SQLite:

```powershell
python manage.py dump_from_sqlite
```

**What this does:**
- Reads data from the SQLite database
- Exports to `backups/data_YYYYMMDD_HHMMSS.json`
- Excludes system tables (contenttypes, permissions, sessions)
- Uses natural foreign keys for better compatibility
- Shows progress and record count

**Expected output:**
```
🗄️  SQLite Data Dump Tool
==================================================
📋 Configuration:
   Source DB: E:\New Downloads\Hammer\myProject\db.sqlite3
   Output file: E:\New Downloads\Hammer\myProject\backups\data_20251021_143045.json
   Database: sqlite

📦 Apps to export: auth.User, auth.Group, myApp
🚫 Excluding: contenttypes, auth.permission, admin.logentry, sessions.session

⏳ Exporting data from SQLite...

✅ Data exported successfully!
   Output: E:\New Downloads\Hammer\myProject\backups\data_20251021_143045.json
   Size: 1,234,567 bytes (1,205.63 KB)
   Records: 1,523

🎉 Export completed successfully!
```

**Note the output filename** - you'll need it for the next step!

### Step 7: Import Data into PostgreSQL

Load the exported data into PostgreSQL:

```powershell
# Replace with your actual filename from Step 6
python manage.py loaddata backups\data_20251021_143045.json
```

**What this does:**
- Reads the JSON fixture file
- Imports all records into PostgreSQL
- Preserves relationships using natural keys
- Shows progress for each model

**Expected output:**
```
Installed 1523 object(s) from 1 fixture(s)
```

**Common Issues:**
- **Integrity errors:** If you see foreign key errors, it might mean some related records weren't exported. Check the excluded models.
- **Duplicate keys:** If you already ran this, you might need to clear the PostgreSQL database first.

### Step 8: Reset PostgreSQL Sequences

After importing data, reset the auto-increment sequences:

```powershell
python manage.py reset_sequences
```

**What this does:**
- Finds all tables with auto-increment primary keys
- Resets sequences to `MAX(id) + 1`
- Prevents duplicate key errors on new inserts

**Expected output:**
```
🔄 PostgreSQL Sequence Reset Tool
==================================================
📋 Configuration:
   Database: default
   Engine: django.db.backends.postgresql

📦 Found 45 models to process

⏳ Generating sequence reset SQL...
   Generated 45 sequence reset commands

⏳ Executing sequence resets...

✅ Successfully reset 45 sequences!

📊 Models processed:
   1. auth.User
   2. auth.Group
   3. myApp.Service
   4. myApp.Project
   ... and 41 more

🎉 Sequence reset completed successfully!
```

### Step 9: Verify Data Migration

Compare record counts between SQLite and PostgreSQL:

```powershell
python manage.py check_counts
```

**What this does:**
- Counts records in each model
- Compares SQLite vs PostgreSQL
- Shows mismatches if any

**Expected output:**
```
📊 Database Record Count Comparison
==================================================
📋 Configuration:
   Source DB: sqlite (django.db.backends.sqlite3)
   Target DB: default (django.db.backends.postgresql)

📦 Checking 25 models...

──────────────────────────────────────────────────────────────────────
Model                                    Source     Target     Status
──────────────────────────────────────────────────────────────────────
auth.User                                5          5          ✓ OK
auth.Group                               3          3          ✓ OK
myApp.Service                            12         12         ✓ OK
myApp.Project                            156        156        ✓ OK
myApp.CaseStudy                          45         45         ✓ OK
... (more models)
──────────────────────────────────────────────────────────────────────
TOTAL                                    1523       1523
──────────────────────────────────────────────────────────────────────

📈 Summary:
   Models checked: 25
   Total records (source): 1,523
   Total records (target): 1,523

✅ All counts match! Migration successful.
```

### Step 10: Test the Application

Start the development server and test functionality:

```powershell
python manage.py runserver
```

**What to test:**
1. **Admin login:** Visit `http://localhost:8000/admin/` and log in
2. **View existing data:** Browse through your models in the admin
3. **Create new records:** Try creating a new record to verify sequences work
4. **Update records:** Edit existing records
5. **Delete records:** Test deletions work correctly
6. **Foreign keys:** Verify relationships are maintained

### Step 11: Verify Model Counts (Quick Check)

You can also do a quick count check from the shell:

```powershell
python manage.py shell -c "from django.apps import apps; print('\n'.join([f'{m._meta.label}: {m.objects.count()}' for m in apps.get_models() if not m._meta.abstract]))"
```

---

## 🎯 Post-Migration Steps

### A. Clean Up (Once Everything Works)

1. **Remove SQLite from settings.py**

   Edit `myProject/settings.py` and remove the dual-database configuration:

   ```python
   # BEFORE (dual-DB):
   DATABASES = {
       'default': dj_database_url.config(...),
       'sqlite': {...}  # ← Remove this
   }
   
   # AFTER (PostgreSQL only):
   DATABASES = {
       'default': dj_database_url.config(
           default=os.getenv('DATABASE_URL'),
           conn_max_age=600,
           conn_health_checks=True,
           ssl_require=True,
       )
   }
   ```

2. **Archive SQLite files**

   Move your SQLite database and backups to a safe location:

   ```powershell
   # Create archive folder
   mkdir backups\archive_sqlite
   
   # Move SQLite database
   move db.sqlite3 backups\archive_sqlite\
   
   # Your JSON and backup files are already in backups/
   ```

3. **Update .gitignore**

   Ensure your `.gitignore` includes:
   ```
   .env
   db.sqlite3
   backups/
   ```

### B. Deploy to Production (Railway)

1. **Set environment variables on Railway:**
   - Go to your Railway project
   - Add the same environment variables from your `.env` file
   - Railway should already have `DATABASE_URL` set

2. **Deploy your code:**
   ```powershell
   git add .
   git commit -m "Migrate to PostgreSQL"
   git push
   ```

3. **Run migrations on Railway:**
   Railway should automatically run migrations, but you can verify in the deployment logs.

---

## 🔄 Rollback Plan (If Something Goes Wrong)

If you encounter issues during migration, you can roll back to SQLite:

### Option 1: Revert settings.py

1. Edit `myProject/settings.py`
2. Remove or comment out the `DATABASE_URL` environment variable check
3. Set `DATABASES['default']` back to SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Option 2: Restore from Backup

If you need to restore the SQLite database:

```powershell
# Restore from backup
copy backups\db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
```

### Option 3: Re-import from JSON

You can re-import data into SQLite from the JSON fixture:

```powershell
# Make sure DATABASE_URL is not set (use SQLite)
python manage.py migrate
python manage.py loaddata backups\data_YYYYMMDD_HHMMSS.json
```

---

## 🐛 Troubleshooting

### Issue: "psycopg2 not installed"

**Solution:**
```powershell
pip install psycopg[binary]
```

### Issue: "relation does not exist"

**Solution:** Run migrations first:
```powershell
python manage.py migrate
```

### Issue: "duplicate key value violates unique constraint"

**Solution:** Reset sequences:
```powershell
python manage.py reset_sequences
```

### Issue: "SSL connection required"

**Solution:** Ensure `ssl_require=True` is set in `dj_database_url.config()` in settings.py

### Issue: Count mismatches in check_counts

**Possible causes:**
- System tables were correctly excluded (this is normal)
- Some records have foreign key issues
- Data was modified between export and import

**Solution:** Review the specific models with mismatches and check if they're critical.

### Issue: Can't connect to Railway database

**Solutions:**
1. Verify the DATABASE_URL is correct in `.env`
2. Check Railway dashboard for database status
3. Ensure your IP is not blocked (Railway databases are publicly accessible by default)
4. Test connection:
   ```powershell
   python manage.py dbshell
   ```

---

## 📊 Expected Timeline

- **Step 1-4 (Setup):** 5-10 minutes
- **Step 5 (Migrate schema):** 1-2 minutes
- **Step 6 (Export data):** 1-5 minutes (depends on data size)
- **Step 7 (Import data):** 2-10 minutes (depends on data size)
- **Step 8 (Reset sequences):** 1 minute
- **Step 9-10 (Verify):** 5-15 minutes
- **Total:** ~15-45 minutes

---

## 📝 Migration Checklist

- [ ] Created `.env` file with DATABASE_URL
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Backed up SQLite database (`python backup_sqlite.py`)
- [ ] Verified dual-DB configuration
- [ ] Ran migrations on PostgreSQL (`python manage.py migrate`)
- [ ] Exported data from SQLite (`python manage.py dump_from_sqlite`)
- [ ] Imported data into PostgreSQL (`python manage.py loaddata`)
- [ ] Reset sequences (`python manage.py reset_sequences`)
- [ ] Verified counts match (`python manage.py check_counts`)
- [ ] Tested application functionality
- [ ] Admin login works
- [ ] Can create new records
- [ ] Foreign keys work correctly
- [ ] Cleaned up settings.py (removed 'sqlite' database)
- [ ] Archived SQLite files
- [ ] Deployed to production (if applicable)

---

## 🆘 Support

If you encounter issues:

1. **Check the error message carefully** - Django usually provides helpful error details
2. **Review the troubleshooting section** above
3. **Check Railway logs** if it's a connection issue
4. **Verify your .env file** has the correct DATABASE_URL
5. **Test with the Django shell:**
   ```powershell
   python manage.py shell
   >>> from django.db import connection
   >>> connection.ensure_connection()
   >>> print("Connected successfully!")
   ```

---

## ✅ Success Criteria

Your migration is successful when:

1. ✅ PostgreSQL schema created (`migrate` succeeds)
2. ✅ Data exported from SQLite (JSON fixture created)
3. ✅ Data imported into PostgreSQL (`loaddata` succeeds)
4. ✅ Sequences reset (no duplicate key errors)
5. ✅ Record counts match between databases
6. ✅ Application runs normally
7. ✅ Can create new records without errors
8. ✅ Admin panel works
9. ✅ All relationships (foreign keys) intact

---

**Good luck with your migration! 🚀**

