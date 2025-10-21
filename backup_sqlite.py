#!/usr/bin/env python3
"""
SQLite Database Backup Script for Django Project

This script automatically creates backups of the SQLite database used by the Django project.
It locates the database from Django settings, creates a backups directory, and generates
timestamped backup files.

Usage:
    python backup_sqlite.py

Requirements:
    - Django project with SQLite database
    - Proper Django settings configuration
"""

import os
import sys
import shutil
import django
from datetime import datetime
from pathlib import Path


def setup_django():
    """Setup Django environment to access settings."""
    # Add the project directory to Python path
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
    
    # Initialize Django
    django.setup()


def get_database_path():
    """Get the SQLite database path from Django settings."""
    from django.conf import settings
    
    db_config = settings.DATABASES['default']
    
    # Check if it's SQLite
    if db_config['ENGINE'] != 'django.db.backends.sqlite3':
        raise ValueError("This script only supports SQLite databases")
    
    # Get the database file path
    db_path = db_config['NAME']
    
    # Handle both string and Path object
    if isinstance(db_path, str):
        db_path = Path(db_path)
    
    return db_path.resolve()


def create_backup_directory():
    """Create backups directory if it doesn't exist."""
    project_dir = Path(__file__).resolve().parent
    backup_dir = project_dir / 'backups'
    
    backup_dir.mkdir(exist_ok=True)
    return backup_dir


def generate_backup_filename():
    """Generate timestamped backup filename."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"db_backup_{timestamp}.sqlite3"


def backup_database():
    """Main function to backup the SQLite database."""
    try:
        # Setup Django environment
        setup_django()
        
        # Get database path
        db_path = get_database_path()
        
        # Check if database file exists
        if not db_path.exists():
            print(f"⚠️  Warning: Database file not found at {db_path}")
            print("   Make sure the Django project is properly configured and the database exists.")
            return False
        
        # Create backup directory
        backup_dir = create_backup_directory()
        
        # Generate backup filename
        backup_filename = generate_backup_filename()
        backup_path = backup_dir / backup_filename
        
        # Copy database file with metadata preservation
        shutil.copy2(db_path, backup_path)
        
        # Print success message
        print(f"✅ Database backup created successfully!")
        print(f"   Source: {db_path}")
        print(f"   Backup: {backup_path}")
        print(f"   Size: {backup_path.stat().st_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating database backup: {str(e)}")
        return False


def main():
    """Main entry point for command-line usage."""
    print("🗄️  SQLite Database Backup Tool")
    print("=" * 50)
    
    success = backup_database()
    
    if success:
        print("\n🎉 Backup completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Backup failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
