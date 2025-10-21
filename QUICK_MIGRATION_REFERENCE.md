# Quick Migration Reference Card

## 🚀 Quick Start (Windows)

### Prerequisites
```powershell
# 1. Create .env file in myProject/ folder
DATABASE_URL=postgresql://postgres:YesuTOqseYfJqYDXmGpobsvnvXrZmJie@tramway.proxy.rlwy.net:16433/railway

# 2. Install dependencies
myenv\Scripts\activate
pip install -r requirements.txt
```

### Migration Commands (Copy & Paste)

```powershell
# Step 1: Backup current SQLite
python backup_sqlite.py

# Step 2: Create PostgreSQL schema
python manage.py migrate

# Step 3: Export from SQLite
python manage.py dump_from_sqlite

# Step 4: Import to PostgreSQL (replace filename with actual output from Step 3)
python manage.py loaddata backups\data_20251021_143045.json

# Step 5: Reset sequences
python manage.py reset_sequences

# Step 6: Verify counts
python manage.py check_counts

# Step 7: Test server
python manage.py runserver
```

## 📋 Command Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `dump_from_sqlite` | Export SQLite → JSON | `python manage.py dump_from_sqlite` |
| `loaddata` | Import JSON → PostgreSQL | `python manage.py loaddata backups\data.json` |
| `reset_sequences` | Fix auto-increment | `python manage.py reset_sequences` |
| `check_counts` | Verify migration | `python manage.py check_counts` |
| `backup_sqlite.py` | Backup database | `python backup_sqlite.py` |

## ⚡ One-Liner Migration

```powershell
python backup_sqlite.py && python manage.py migrate && python manage.py dump_from_sqlite && python manage.py loaddata backups\data_*.json && python manage.py reset_sequences && python manage.py check_counts
```
**Note:** This assumes PowerShell 7+. For older PowerShell, run each command separately.

## 🔧 Troubleshooting

### Can't connect to PostgreSQL?
```powershell
# Check if .env exists and has DATABASE_URL
Get-Content .env

# Test connection
python manage.py dbshell
```

### Sequences causing errors?
```powershell
python manage.py reset_sequences
```

### Counts don't match?
```powershell
python manage.py check_counts --fail-on-mismatch
```

## 🔙 Rollback

### Quick rollback to SQLite:
```powershell
# Option 1: Remove DATABASE_URL from .env (comment it out)
# Option 2: Restore backup
copy backups\db_backup_20251021_*.sqlite3 db.sqlite3
```

## ✅ Verification Checklist

- [ ] `.env` file created with DATABASE_URL
- [ ] Dependencies installed
- [ ] SQLite backup created
- [ ] PostgreSQL schema created (migrate ran)
- [ ] Data exported (JSON file created)
- [ ] Data imported (loaddata ran)
- [ ] Sequences reset
- [ ] Counts verified (all match)
- [ ] Admin login works
- [ ] Can create new records

## 📁 File Locations

```
myProject/
├── .env                          ← Create this with DATABASE_URL
├── db.sqlite3                    ← Original SQLite database
├── backups/
│   ├── db_backup_*.sqlite3       ← SQLite backups
│   └── data_*.json               ← Data exports
├── manage.py                     ← Modified to load .env
├── myProject/
│   └── settings.py               ← Modified for dual-DB
└── myApp/
    └── management/
        └── commands/
            ├── dump_from_sqlite.py   ← Export command
            ├── reset_sequences.py    ← Sequence reset
            └── check_counts.py       ← Verification
```

## 🎯 Success Criteria

Migration is successful when:
1. ✅ `check_counts` shows all matches
2. ✅ Admin login works
3. ✅ Can create new records without errors
4. ✅ All foreign key relationships intact

## 📞 Help

- **Detailed guide:** See `MIGRATION_STEPS.md`
- **Changes made:** See `MIGRATION_CHANGES_SUMMARY.md`
- **Django errors:** Run with `--traceback` flag
- **Database connection:** Check Railway dashboard

## ⚙️ Environment Variables

**Required in `.env`:**
```env
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:PORT/DATABASE
```

**Optional (if not in settings.py):**
```env
DJANGO_SETTINGS_MODULE=myProject.settings
CLOUDINARY_CLOUD_NAME=your_value
CLOUDINARY_API_KEY=your_value
CLOUDINARY_API_SECRET=your_value
```

## 🔒 Security Notes

- ✅ `.env` should be in `.gitignore`
- ✅ Never commit database credentials
- ✅ Use Railway's environment variables in production
- ✅ Keep backups in a secure location

## 📊 Expected Timeline

- Setup (Steps 1-2): **5 minutes**
- Migration (Steps 3-6): **10-20 minutes**
- Testing (Step 7): **10 minutes**
- **Total: ~25-35 minutes**

---

**Ready to migrate? Start with `MIGRATION_STEPS.md` for detailed instructions!**

