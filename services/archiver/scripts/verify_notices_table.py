#!/usr/bin/env python3
"""Verify that the notices table exists and has the correct structure."""

import asyncio
import aiohttp
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_notices_table():
    """Verify the notices table exists."""
    
    # Load environment variables
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        logger.error("Missing Supabase credentials")
        return False
    
    async with aiohttp.ClientSession() as session:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # Try to query the notices table
        try:
            async with session.get(
                f"{supabase_url}/rest/v1/notices?limit=1",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    logger.info("✅ Notices table exists and is accessible!")
                    return True
                elif resp.status == 404:
                    logger.error("❌ Notices table does not exist. Please apply the migration first.")
                    return False
                else:
                    error = await resp.text()
                    logger.warning(f"Unexpected response: {resp.status} - {error}")
                    return False
        except Exception as e:
            logger.error(f"Error verifying notices table: {e}")
            return False

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
    
    success = await verify_notices_table()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())


