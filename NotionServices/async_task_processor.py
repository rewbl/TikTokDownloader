"""
简化的新视频处理模块
使用线程处理Slack通知和Notion记录创建
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '99notion-base'))

from concurrent.futures import ThreadPoolExecutor
from StudioY.FavoriteVideoDto import FavoriteVideoDto
from Slack.SlackDouyinMonitor import send_slack_notification
from .douyin_post_service import NotionDouyinPostService

# 全局线程池
_thread_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="video_processor")


async def process_new_video(video: FavoriteVideoDto, account_page_id: str, account_name: str = None, slack_channel: str = 'vivian'):
    """
    处理新视频：创建Notion记录并发送Slack通知
    使用线程池处理，避免阻塞主事件循环

    Args:
        video: 视频数据
        account_page_id: 关联的账号页面ID
        account_name: 账号名称（用于生成页面标题）
        slack_channel: Slack通知频道
    """
    # 使用线程池提交任务
    future = _thread_pool.submit(_handle_new_video_sync, video, account_page_id, account_name, slack_channel)
    print(f"已提交新视频处理任务到线程池: {video.AwemeId}")
    return future


def _handle_new_video_sync(video: FavoriteVideoDto, account_page_id: str, account_name: str, slack_channel: str):
    """
    同步处理新视频的函数（在线程中运行）

    Args:
        video: 视频数据
        account_page_id: 关联的账号页面ID
        account_name: 账号名称
        slack_channel: Slack通知频道
    """
    post_service = NotionDouyinPostService()

    try:
        # 1. 创建Notion记录
        page_id = post_service.create_post_from_video(video, account_page_id, account_name)

        if page_id:
            print(f"成功创建Notion记录: {video.AwemeId}")
        else:
            print(f"创建Notion记录失败: {video.AwemeId}")

        # 2. 发送Slack通知（即使失败也不影响主流程）
        try:
            text, blocks = video.notification_summary()
            # 在线程中运行异步Slack通知
            success = _send_slack_notification_sync(slack_channel, text, blocks)

            if success:
                print(f"成功发送Slack通知: {video.AwemeId}")
            else:
                print(f"发送Slack通知失败: {video.AwemeId}")
        except Exception as slack_error:
            print(f"Slack通知异常: {slack_error}")
            # Slack失败不影响主流程

    except Exception as e:
        print(f"处理新视频失败: {e}")
        import traceback
        traceback.print_exc()


def _send_slack_notification_sync(slack_channel: str, text: str, blocks) -> bool:
    """
    在线程中同步发送Slack通知

    Args:
        slack_channel: Slack频道
        text: 消息文本
        blocks: 消息块

    Returns:
        是否发送成功
    """
    try:
        # 在新的事件循环中运行异步函数
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(send_slack_notification(slack_channel, text, blocks))
            return result
        finally:
            loop.close()
    except Exception as e:
        print(f"同步Slack通知失败: {e}")
        return False
