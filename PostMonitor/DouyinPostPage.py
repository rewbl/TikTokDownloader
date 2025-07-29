import pytz
from notion_base import NotionPageBase
from datetime import datetime


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
    

    @classmethod
    def create_from_favorite_video(cls, video_dto, account_page_id: str, account_name: str = None):
        china_tz = pytz.timezone('Asia/Shanghai')
        dt = datetime.fromtimestamp(video_dto.CreateTime, tz=china_tz)
        create_date = dt.isoformat()
        time_str = dt.strftime('%m-%d %H:%M:%S')
        page_name = f"{account_name} - 新视频 {time_str}"

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
            "Duration": int(video_dto.Duration),
            "Date": create_date
        }


class DouyinAccountPage(NotionPageBase):
    DATABASE_ID = "23e035de0731804aaf4ac18652c62393"
