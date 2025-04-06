from prefect import task, flow
import sys
import asyncio
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@task(retries=3, retry_delay_seconds=60)
async def run_crawler(script_path: str, description: str) -> bool:
    """Run a crawler script with retries"""
    try:
        logger.info(f"Starting {description}...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            logger.info(f"{description} completed successfully")
            return True
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise Exception(f"{description} failed: {error_msg}")
    except Exception as e:
        logger.error(f"Error in {description}: {str(e)}")
        raise

@task(retries=2)
async def start_api_server():
    """Start the FastAPI server as a task"""
    import uvicorn
    config = uvicorn.Config("api.main:app", port=8000, log_level="info", reload=True)
    server = uvicorn.Server(config)
    await server.serve()

@flow(name="Property Data Pipeline")
async def property_pipeline():
    """Main flow that orchestrates the property data collection and processing"""
    tasks = [
        ("app.py", "Housing.com crawler"),
        ("magicbricks_app.py", "MagicBricks crawler"),
        ("agents/extract_properties.py", "Property data extraction"),
    ]
    
    for script_path, description in tasks:
        await run_crawler(script_path, description)
    
    logger.info("Property pipeline completed successfully")