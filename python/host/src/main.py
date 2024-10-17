import asyncio
from src.test_system import TestSystem

import logging
logger = logging.getLogger(__name__)

async def main():
    logging.basicConfig(level=logging.INFO)

    logger.info("Host starting...")

    system = TestSystem()
    system.initialise()
    await system.run_processes()


if __name__ == '__main__':
    asyncio.run(main())
