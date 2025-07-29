"""
NotionServices - Notion数据库服务模块
提供抖音账号和视频的Notion数据库操作
"""

from .douyin_account_page import DouyinAccountNotionPage
from .douyin_post_page import DouyinPostNotionPage
from .douyin_account_service import NotionDouyinAccountService
from .douyin_post_service import NotionDouyinPostService

# 延迟导入，避免Slack依赖问题
def get_process_new_video():
    """延迟导入process_new_video函数"""
    from .async_task_processor import process_new_video
    return process_new_video

__all__ = [
    "DouyinAccountNotionPage",
    "DouyinPostNotionPage",
    "NotionDouyinAccountService",
    "NotionDouyinPostService",
    "get_process_new_video"
]
