#!/usr/bin/env python3
"""Apply notices table migration via Supabase."""

import asyncio
import aiohttp
import os
import sys
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_migration_via_psql():
    """Try to apply migration via psql if connection string is available."""
    # Try to get connection string from environment
    db_url = os.getenv('DATABASE_URL') or os.getenv('SUPABASE_DB_URL')
    
    if not db_url:
        logger.warning("DATABASE_URL or SUPABASE_DB_URL not found, skipping psql method")
        return False
    
    migration_path = "/home/matrix-ai/services/archiver/data/migrations/004_notices_table.sql"
    
    try:
        logger.info("Attempting to apply migration via psql...")
        result = subprocess.run(
            ['psql', db_url, '-f', migration_path],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Migration applied successfully via psql!")
        logger.info(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"psql execution failed: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.warning("psql not found, skipping psql method")
        return False

def print_manual_instructions():
    """Print instructions for manual migration application."""
    migration_path = "/home/matrix-ai/services/archiver/data/migrations/004_notices_table.sql"
    
    print("\n" + "="*70)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("="*70)
    print("\nSince Supabase doesn't support direct SQL execution via REST API,")
    print("please apply the migration using one of these methods:\n")
    print("METHOD 1: Supabase Dashboard (Recommended)")
    print("-" * 70)
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Copy and paste the contents of:")
    print(f"   {migration_path}")
    print("4. Click 'Run' to execute the migration\n")
    print("METHOD 2: Supabase CLI")
    print("-" * 70)
    print("1. Install Supabase CLI if not already installed")
    print("2. Run: supabase db push")
    print("   Or: supabase db execute < migration_file.sql\n")
    print("METHOD 3: psql (if you have direct database access)")
    print("-" * 70)
    print("1. Get your connection string from Supabase dashboard")
    print("2. Run: psql 'your-connection-string' -f", migration_path)
    print("\n" + "="*70 + "\n")
    
    # Also print the SQL content
    try:
        with open(migration_path, 'r') as f:
            sql_content = f.read()
        print("SQL Migration Content:")
        print("-" * 70)
        print(sql_content)
        print("-" * 70)
    except Exception as e:
        logger.error(f"Failed to read migration file: {e}")

async def main():
    """Main entry point."""
    # Load environment from env file
    env_file = "/home/matrix-ai/services/archiver/config/env"
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value
    except Exception as e:
        logger.warning(f"Failed to load environment file: {e}")
    
    # Try psql method first
    success = await apply_migration_via_psql()
    
    if not success:
        print_manual_instructions()
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())


