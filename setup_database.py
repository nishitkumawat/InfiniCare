#!/usr/bin/env python
"""
Database setup script for the Reve Digital Platform

This script creates the necessary database tables for the Reve Digital Platform.
It can be used with either SQLite (for development) or MySQL (for production).

Usage:
    python setup_database.py [--mysql]

Options:
    --mysql     Use MySQL instead of SQLite (requires mysqlclient package and a running MySQL server)

Requirements:
    - Python 3.9+
    - Django 5.0+
    - mysqlclient (if using MySQL)
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_sqlite():
    """Set up SQLite database"""
    print("Setting up SQLite database...")
    try:
        # Run Django migrations
        os.chdir('farmtech_project')
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("SQLite database setup complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error setting up SQLite database: {e}")
        return False

def setup_mysql():
    """Set up MySQL database"""
    print("Setting up MySQL database...")
    
    db_name = input("Enter MySQL database name [reve_digital_platform]: ") or "reve_digital_platform"
    db_user = input("Enter MySQL username [root]: ") or "root"
    db_password = input("Enter MySQL password []: ")
    db_host = input("Enter MySQL host [localhost]: ") or "localhost"
    db_port = input("Enter MySQL port [3306]: ") or "3306"
    
    # Create .env file for MySQL settings
    env_file = Path(".env")
    env_content = f"""
DB_ENGINE=django.db.backends.mysql
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("Created .env file with database settings")
    
    # Create database if it doesn't exist
    try:
        import mysql.connector
        
        # Connect to MySQL server
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created or already exists")
        
        # Close connection
        cursor.close()
        conn.close()
        
        # Apply SQL schema
        schema_file = Path("database_schema.sql")
        if schema_file.exists():
            print("Applying database schema...")
            # Remove CREATE DATABASE statements from schema file for safety
            with open(schema_file, "r") as f:
                schema = f.read()
            
            # Create a temporary file with only the table definitions
            temp_schema_file = Path("temp_schema.sql")
            with open(temp_schema_file, "w") as f:
                for line in schema.split("\n"):
                    if not line.strip().startswith("CREATE DATABASE") and not line.strip().startswith("USE"):
                        f.write(line + "\n")
            
            # Apply schema
            try:
                subprocess.run([
                    "mysql",
                    f"-h{db_host}",
                    f"-P{db_port}",
                    f"-u{db_user}",
                    f"-p{db_password}" if db_password else "",
                    db_name,
                    "-e",
                    f"source {temp_schema_file}"
                ], check=True)
                print("Database schema applied successfully")
            except subprocess.CalledProcessError as e:
                print(f"Error applying schema: {e}")
                
            # Remove temporary file
            if temp_schema_file.exists():
                temp_schema_file.unlink()
        
        # Run Django migrations
        os.chdir('farmtech_project')
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        subprocess.run([sys.executable, 'manage.py', 'migrate'], check=True)
        print("MySQL database setup complete!")
        return True
        
    except ImportError:
        print("MySQL connector not found. Please install with: pip install mysql-connector-python")
        return False
    except Exception as e:
        print(f"Error setting up MySQL database: {e}")
        return False

def create_superuser():
    """Create a Django superuser"""
    print("\nWould you like to create a superuser? (y/n)")
    if input().lower() == 'y':
        try:
            os.chdir('farmtech_project')
            subprocess.run([sys.executable, 'manage.py', 'createsuperuser'], check=False)
        except Exception as e:
            print(f"Error creating superuser: {e}")

def main():
    parser = argparse.ArgumentParser(description="Database setup script for Reve Digital Platform")
    parser.add_argument('--mysql', action='store_true', help='Use MySQL instead of SQLite')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Reve Digital Platform - Database Setup")
    print("=" * 60)
    
    # Make sure we're in the project root
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)
    
    if args.mysql:
        success = setup_mysql()
    else:
        success = setup_sqlite()
    
    if success:
        create_superuser()
        
        print("\nDatabase setup complete!")
        print("\nYou can now run the development server with:")
        print("cd farmtech_project")
        print("python manage.py runserver 0.0.0.0:5000")
    else:
        print("\nDatabase setup failed. Please check the error messages and try again.")

if __name__ == "__main__":
    main()