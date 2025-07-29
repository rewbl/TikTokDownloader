"""
NotionDouyinPostService - 抖音视频Notion数据库服务
负责创建和管理抖音视频记录
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '99notion-base'))

from typing import List, Optional, Set, Dict
from notion_base import NotionDatabase
from StudioY.FavoriteVideoDto import FavoriteVideoDto
from datetime import datetime
from .douyin_post_page import DouyinPostNotionPage


class NotionDouyinPostService:
    """
    抖音视频Notion数据库服务
    提供视频记录的创建和查询功能
    """
    
    def __init__(self):
        """初始化服务"""
        # 使用NOTION_POST_BOT_API_KEY来访问抖音相关数据库
        from notion_base.config import NOTION_POST_BOT_API_KEY
        self.database = NotionDatabase(NOTION_POST_BOT_API_KEY, DouyinPostNotionPage.DATABASE_ID)
    
    def create_post_from_video(self, video_dto: FavoriteVideoDto, account_page_id: str, account_name: str = None) -> Optional[str]:
        """
        从FavoriteVideoDto创建视频记录

        Args:
            video_dto: 视频数据传输对象
            account_page_id: 关联的账号页面ID
            account_name: 账号名称（用于生成页面标题）

        Returns:
            创建的页面ID，如果创建失败则返回None
        """
        try:
            # 使用DouyinPostNotionPage的工厂方法创建数据
            page_data = DouyinPostNotionPage.create_from_favorite_video(video_dto, account_page_id, account_name)

            # 创建Notion页面
            result = self.database.create_from_dict(page_data)
            
            if result and 'id' in result:
                print(f"成功创建视频记录: {video_dto.AwemeId}")
                return result['id']
            else:
                print(f"创建视频记录失败: {video_dto.AwemeId}")
                return None
                
        except Exception as e:
            print(f"创建视频记录异常: {e}")
            return None
    
    def get_existing_aweme_ids_for_account(self, account_page_id: str) -> Set[str]:
        """
        获取指定账号已存在的视频ID集合
        按Date降序排列，只获取最新的100个视频用于重复检查

        Args:
            account_page_id: 账号页面ID

        Returns:
            已存在的视频ID集合（最新100个）
        """
        try:
            # 使用原始API查询，添加排序和分页
            filter_condition = {
                "property": "Account",
                "relation": {
                    "contains": account_page_id
                }
            }

            # 添加排序条件：按Date降序排列
            sorts = [
                {
                    "property": "Date",
                    "direction": "descending"
                }
            ]

            response = self.database.client.databases.query(
                database_id=self.database.database_id,
                filter=filter_condition,
                sorts=sorts,
                page_size=100  # 限制返回最新100个视频
            )

            # 转换结果为字典格式
            results = response.get('results', [])
            dict_results = self.database.pages_to_dict(results)

            aweme_ids = set()
            for result in dict_results:
                aweme_id = result.get('Aweme Id')
                if aweme_id:
                    aweme_ids.add(aweme_id)

            print(f"账号 {account_page_id[:20]}... 加载了最新 {len(aweme_ids)} 个视频ID用于重复检查")
            return aweme_ids

        except Exception as e:
            print(f"获取已存在视频ID失败: {e}")
            return set()
    
    def check_aweme_id_exists(self, aweme_id: str) -> bool:
        """
        检查指定的视频ID是否已存在

        Args:
            aweme_id: 视频ID

        Returns:
            是否存在
        """
        try:
            result = (self.database
                     .where('Aweme Id')
                     .equals(aweme_id)
                     .exists())

            return result

        except Exception as e:
            print(f"检查视频ID是否存在失败: {e}")
            return False
