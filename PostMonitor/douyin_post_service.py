
from typing import Optional, Set

from notion_base import get_database

from PostMonitor.DouyinPostPage import DouyinPostNotionPage
from StudioY.FavoriteVideoDto import FavoriteVideoDto


class NotionDouyinPostService:

    def __init__(self):
        self.database =get_database(DouyinPostNotionPage.DATABASE_ID)
    
    def create_post_from_video(self, video_dto: FavoriteVideoDto, account_page_id: str, account_name: str = None) -> Optional[str]:
        try:
            page_data = DouyinPostNotionPage.create_from_favorite_video(video_dto, account_page_id, account_name)
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

        try:
            results = (self.database
                      .where('Account')
                      .contains(account_page_id)
                      .order_by_desc('Date')
                      .limit(100))
            aweme_ids = set()
            for result in results:
                aweme_id = result.get('Aweme Id')
                if aweme_id:
                    aweme_ids.add(aweme_id)
            return aweme_ids
        except Exception as e:
            print(f"获取已存在视频ID失败: {e}")
            return set()
