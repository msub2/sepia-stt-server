"""Module to lauch server with specific settings
More info: https://www.uvicorn.org/deployment/
"""

import asyncio
from hypercorn.asyncio import serve
from hypercorn.config import Config
from server import app


# Parse commandline arguments and create the settings instance
from launch_setup import settings
config = Config()
config.bind = [f'{settings.host}:{settings.port}']
config.loglevel = settings.log_level
config.use_reloader = settings.code_reload

def main():
    """Main method to start server"""
    asyncio.run(serve(app, config))
    print("SEPIA STT Server - Starting...")

# Run if this is called as main
if __name__ == "__main__":
    main()
