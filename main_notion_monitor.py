

import asyncio
import logging
import sys
from datetime import datetime
from PostMonitor.NotionDouyinPostMonitor import NotionDouyinPostMonitor


def setup_logging():
    """设置日志记录"""
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'notion_monitor_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
        ]
    )

    return logging.getLogger(__name__)


async def main():
    monitor = NotionDouyinPostMonitor()
    await monitor.start()
    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
