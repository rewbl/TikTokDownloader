"""
主程序 - 运行基于Notion的抖音视频监控器
功能：
- 从Notion数据库获取要监控的账号（67个账号）
- 每分钟自动刷新账号列表，支持动态添加/移除
- 检测新视频并创建Notion记录
- 使用线程池处理，避免阻塞主循环
- 发送Slack通知（可选）
"""

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
    """主函数"""
    logger = setup_logging()
    logger.info("启动基于Notion的抖音视频监控器...")
    logger.info("监控功能：67个账号，自动检测新视频，创建Notion记录")

    # 创建监控器
    monitor = NotionDouyinPostMonitor()

    try:
        logger.info("正在启动监控器...")

        # 运行监控器
        await monitor.run_forever()

    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭监控器...")

    except Exception as e:
        logger.error(f"监控器运行时发生错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

    finally:
        try:
            await monitor.stop()
            logger.info("监控器已停止")
        except Exception as e:
            logger.error(f"停止监控器时发生错误: {e}")


async def test_run():
    """测试运行 - 只运行5分钟"""
    logger = setup_logging()
    logger.info("启动测试模式（5分钟）...")

    monitor = NotionDouyinPostMonitor()

    try:
        await monitor.start()
        logger.info("监控器已启动，将运行5分钟...")

        # 运行5分钟
        await asyncio.sleep(300)
        logger.info("测试时间结束")

    except Exception as e:
        logger.error(f"测试运行时发生错误: {e}")
        import traceback
        logger.error(f"错误详情: {traceback.format_exc()}")

    finally:
        await monitor.stop()
        logger.info("测试运行结束")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # 测试模式：python main_notion_monitor.py test
        asyncio.run(test_run())
    else:
        # 正常模式：python main_notion_monitor.py
        asyncio.run(main())
