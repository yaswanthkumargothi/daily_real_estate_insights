import asyncio
import logging
import sys
import os
from datetime import datetime
import subprocess
import uvicorn
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.property_tasks import property_pipeline, start_api_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

async def run_script(script_path: str, description: str) -> bool:
    """Run a Python script and return success status"""
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
            logger.error(f"{description} failed with return code {process.returncode}")
            logger.error(f"Error output: {stderr.decode()}")
            return False
    except Exception as e:
        logger.error(f"Error running {description}: {str(e)}")
        return False

async def daily_job():
    """Run all tasks in sequence"""
    logger.info("Starting daily job execution")
    
    tasks = [
        ("app.py", "Housing.com crawler"),
        ("magicbricks_app.py", "MagicBricks crawler"),
        ("agents/extract_properties.py", "Property data extraction"),
    ]
    
    for script_path, description in tasks:
        success = await run_script(script_path, description)
        if not success:
            logger.error(f"Daily job stopped due to failure in {description}")
            return
    
    logger.info("Daily job completed successfully")

def start_api_server():
    """Start the FastAPI server"""
    try:
        # Start uvicorn server in a separate process
        uvicorn.run(
            "api.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    except Exception as e:
        logger.error(f"Error starting API server: {str(e)}")

async def main():
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Create deployment for the property pipeline
    deployment = Deployment.build_from_flow(
        flow=property_pipeline,
        name="daily-property-crawler",
        schedule=CronSchedule(cron="0 1 * * *"),  # Run at 1 AM daily
        tags=["production"]
    )
    
    # Apply the deployment
    deployment.apply()
    
    # Start the API server
    start_api_server()
    
    try:
        # Keep the script running
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutdown")

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)