"""
DouyinPostNotionPage - 抖音视频页面强类型类
对应Notion中的Douyin Posts数据库
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '99notion-base'))

from notion_base import NotionPageBase
from datetime import datetime
from typing import Optional


class DouyinPostNotionPage(NotionPageBase):
    """
    抖音视频页面强类型类
    
    对应Notion数据库字段：
    - Account: 关联的抖音账号 (relation类型)
    - Aweme Id: 视频ID (text类型)
    - Best Rate Url: 最佳码率视频链接 (url类型)
    - Caption: 视频标题 (text类型)
    - Description: 视频描述 (text类型)
    - Cover Url: 封面图片链接 (url类型)
    - Height: 视频高度 (number类型)
    - Width: 视频宽度 (number类型)
    - Duration: 视频时长(秒) (number类型)
    - Date: 创建日期 (date类型)
    
    使用示例:
        post.Account = ["account_page_id"]
        post.Aweme_Id = "7123456789"
        post.Caption = "视频标题"
        post.Description = "视频描述"
        post.Best_Rate_Url = "https://..."
        post.Cover_Url = "https://..."
        post.Height = 1920
        post.Width = 1080
        post.Duration = 30
        post.Date = "2024-01-01"
    """
    
    DATABASE_ID = "23e035de0731803c9609e369fdbcc16d"
    
    def get_display_name(self) -> str:
        """获取页面显示名称"""
        return getattr(self, 'Caption', None) or f"Post-{self.page_id[:8]}"
    
    @classmethod
    def create_from_favorite_video(cls, video_dto, account_page_id: str, account_name: str = None):
        """
        从FavoriteVideoDto创建Notion页面数据

        Args:
            video_dto: FavoriteVideoDto实例
            account_page_id: 关联的账号页面ID
            account_name: 账号名称（用于生成页面标题）

        Returns:
            用于创建Notion页面的数据字典
        """
        # 将Unix时间戳转换为ISO 8601日期时间字符串（包含时间到秒）
        create_date = None
        page_name = None

        if video_dto.CreateTime:
            # 使用ISO 8601格式，包含完整的日期时间信息
            # 确保使用正确的时区（中国时区 UTC+8）
            import pytz
            china_tz = pytz.timezone('Asia/Shanghai')
            dt = datetime.fromtimestamp(video_dto.CreateTime, tz=china_tz)
            create_date = dt.isoformat()

            # 生成页面名称：account name - 新视频 mm-dd hh:mm:ss
            # 使用中国时区的时间
            time_str = dt.strftime('%m-%d %H:%M:%S')
            if account_name:
                page_name = f"{account_name} - 新视频 {time_str}"
            else:
                page_name = f"新视频 {time_str}"
        else:
            # 如果没有时间信息，使用账号名称和视频ID
            if account_name:
                page_name = f"{account_name} - 新视频 {video_dto.AwemeId}"
            else:
                page_name = f"新视频 {video_dto.AwemeId}"

        return {
            "Name": page_name,  # 页面标题
            "Account": [account_page_id],  # 关系类型
            "Aweme Id": video_dto.AwemeId,
            "Best Rate Url": video_dto.BestBitRateUrl,
            "Caption": video_dto.Caption,
            "Description": video_dto.Description,
            "Cover Url": video_dto.CoverUrl,
            "Height": video_dto.Height,
            "Width": video_dto.Width,
            "Duration": int(video_dto.Duration/1000),
            "Date": create_date
        }
