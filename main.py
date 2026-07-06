import restate
import asyncio
import hypercorn.asyncio
from hypercorn.config import Config
from dotenv import load_dotenv

# Import our service
from restate_service import legal_agent_service

# Load environment variables from .env file
load_dotenv()

# Create the Restate endpoint and register our service
app = restate.app(services=[legal_agent_service])

if __name__ == "__main__":
    # Start the server on port 9080 (default for Restate endpoints)
    print("[Restate] LegalAgent Service starting on port 9080...")
    config = Config()
    config.bind = ["0.0.0.0:9080"]
    asyncio.run(hypercorn.asyncio.serve(app, config))
