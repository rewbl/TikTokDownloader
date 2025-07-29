"""
NotionDouyinAccountService - 抖音账号Notion数据库服务
负责从Notion获取要监控的抖音账号
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '99notion-base'))

from typing import List, Dict, Optional
from notion_base import NotionDatabase
from .douyin_account_page import DouyinAccountNotionPage


class NotionDouyinAccountService:
    """
    抖音账号Notion数据库服务
    提供账号查询和管理功能
    """
    
    def __init__(self):
        """初始化服务"""
        # 使用NOTION_POST_BOT_API_KEY来访问抖音相关数据库
        from notion_base.config import NOTION_POST_BOT_API_KEY
        self.database = NotionDatabase(NOTION_POST_BOT_API_KEY, DouyinAccountNotionPage.DATABASE_ID)
    
    def get_monitor_accounts(self) -> List[Dict[str, str]]:
        """
        获取所有需要监控的抖音账号
        直接在Notion查询中过滤带"Monitor Posts"标签的账号

        Returns:
            账号列表，每个账号包含：
            - page_id: Notion页面ID
            - name: 账号昵称
            - sec_uid: 账号SecUid
        """
        try:
            # 直接查询包含"Monitor Posts"标签且有必要字段的账号
            results = (self.database
                      .where('Tags')
                      .contains('Monitor Posts')
                      .where('SecUid')
                      .is_not_empty()
                      .where('Name')
                      .is_not_empty()
                      .all())

            accounts = []
            for result in results:
                # 从原始数据中获取page_id
                page_id = result.get('id') or result.get('page_id')
                accounts.append({
                    'page_id': page_id,
                    'name': result['Name'],
                    'sec_uid': result['SecUid']
                })

            return accounts

        except Exception as e:
            print(f"获取监控账号失败: {e}")
            return []
    
    def get_account_by_sec_uid(self, sec_uid: str) -> Optional[Dict[str, str]]:
        """
        根据SecUid获取账号信息
        
        Args:
            sec_uid: 账号的SecUid
            
        Returns:
            账号信息字典，如果未找到则返回None
        """
        try:
            result = (self.database
                     .where('SecUid')
                     .equals(sec_uid)
                     .first())
            
            if result:
                page_id = result.get('id') or result.get('page_id')
                return {
                    'page_id': page_id,
                    'name': result['Name'],
                    'sec_uid': result['SecUid']
                }
            return None
            
        except Exception as e:
            print(f"根据SecUid获取账号失败: {e}")
            return None
    
    def get_account_page_id_by_sec_uid(self, sec_uid: str) -> Optional[str]:
        """
        根据SecUid获取账号的Notion页面ID
        
        Args:
            sec_uid: 账号的SecUid
            
        Returns:
            Notion页面ID，如果未找到则返回None
        """
        account = self.get_account_by_sec_uid(sec_uid)
        return account['page_id'] if account else None
