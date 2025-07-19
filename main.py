#!/usr/bin/env python3
"""
Main entry point for WoW Class Learner Server
"""

import logging
from pkg.server import create_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    # Create and setup server
    server = create_server()
    
    if server.setup():
        # Run the server
        server.run()
    else:
        logger.error("Failed to setup server. Exiting.")
        exit(1)

if __name__ == "__main__":
    main()
