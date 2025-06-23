"""Main application entry point."""

import sys
from pathlib import Path


# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))


if __name__ == "__main__":
    import uvicorn

    from config import config

    uvicorn.run("main:app", host=config.API_HOST, port=config.API_PORT, reload=config.API_DEBUG)
