#!/usr/bin/env python3
"""
Database setup script for KrishiQuery
Creates all tables and initializes the database schema
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.db_connection import engine, Base
from backend.config import settings
from backend.services import farmer_service  # noqa: F401 - imports ORM models into Base metadata
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database(drop_existing=False):
    """Setup database tables"""
    
    logger.info("Setting up KrishiQuery database...")
    logger.info(f"Database URL: {settings.DATABASE_URL.replace('://', '://***:***@') if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
    
    try:
        if drop_existing:
            logger.warning("Dropping all existing tables...")
            Base.metadata.drop_all(bind=engine)
            logger.info("All tables dropped")
        
        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully")
        
        # Verify connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("Database connection verified")
        
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        return False

def run_sql_file(sql_file_path):
    """Run SQL file on database"""
    try:
        with engine.connect() as conn:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
                # Split by semicolon and execute each statement
                for statement in sql_script.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                        conn.commit()
        logger.info(f"SQL file {sql_file_path} executed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to run SQL file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Setup KrishiQuery database")
    parser.add_argument("--drop", action="store_true", help="Drop existing tables before creating")
    parser.add_argument("--schema-file", type=str, help="Path to schema SQL file (optional)")
    
    args = parser.parse_args()
    
    if args.schema_file:
        if run_sql_file(args.schema_file):
            logger.info("Database setup from SQL file completed")
        else:
            logger.error("Database setup from SQL file failed")
            sys.exit(1)
    else:
        if setup_database(drop_existing=args.drop):
            logger.info("Database setup completed successfully")
        else:
            logger.error("Database setup failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
