import html
import json
from typing import Optional, Tuple, List, Dict

from pydantic import BaseModel


class DouyinAuthorDto(BaseModel):
    Uid: Optional[str] = None
    SecUid: Optional[str] = None
    AvatarUrl: Optional[str] = None
    AvatarThumbUrl: Optional[str] = None
    Nickname: Optional[str] = None

    @staticmethod
    def from_dict(author: dict) -> 'DouyinAuthorDto':
        return DouyinAuthorDto(
            Uid=author['uid'],
            SecUid=author['sec_uid'],
            Nickname=author['nickname'],
            AvatarUrl=author.get('avatar_larger', {}).get('url_list', [None])[0],
            AvatarThumbUrl=author.get('avatar_thumb', {}).get('url_list', [None])[0]
        )


class FavoriteVideoDto(BaseModel):
    Author: Optional[DouyinAuthorDto] = None
    AwemeId: Optional[str] = None
    Caption: Optional[str] = None
    Description: Optional[str] = None
    Height: Optional[int] = None
    Width: Optional[int] = None
    CoverUrl: Optional[str] = None
    Duration: Optional[int] = None
    Ratio: Optional[str] = None
    BestBitRateUrl: Optional[str] = None
    CreateTime: Optional[int] = None
    CollectCount: Optional[int] = None
    CommentCount: Optional[int] = None
    DiggCount: Optional[int] = None
    ShareCount: Optional[int] = None

    @staticmethod
    def from_dict(aweme: dict) -> 'FavoriteVideoDto':
        cover_urls = aweme.get('video', {}).get('cover', {}).get('url_list', [])
        return FavoriteVideoDto(
            Author=DouyinAuthorDto.from_dict(aweme.get('author', {})),
            AwemeId=aweme['aweme_id'],
            Caption=aweme['caption'],
            Description=aweme['desc'],
            Height=aweme['video']['height'],
            Width=aweme['video']['width'],
            Duration=aweme['video']['duration'],
            CoverUrl=cover_urls[1] if len(cover_urls) > 1 else cover_urls[0] if len(cover_urls) > 0 else '',
            Ratio=aweme.get('video', {}).get('ratio', 0),
            BestBitRateUrl=aweme['video']['bit_rate'][0]['play_addr']['url_list'][-1],
            CreateTime=aweme['create_time'],
            CollectCount=aweme['statistics']['collect_count'],
            CommentCount=aweme['statistics']['comment_count'],
            DiggCount=aweme['statistics']['digg_count'],
            ShareCount=aweme['statistics']['share_count']
        )

    def sanitize_text(self, text: str) -> str:
        return html.escape(text)

    def notification_summary(self) -> Tuple[str, List[Dict]]:
        sanitized_caption = self.sanitize_text(self.Caption)
        sanitized_nickname = self.sanitize_text(self.Author.Nickname)
        sanitized_description = self.sanitize_text(self.Description)
        text = f'*{sanitized_nickname}* 发布了视频：*{sanitized_description}* *{sanitized_caption}*'
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'*{sanitized_nickname}* 发布了视频： \n*{sanitized_description}* \n *{sanitized_caption}* \n *封面图片地址：*'
                }
            },
            # {
            #     "type": "image",
            #     "image_url": self.CoverUrl,
            #     "alt_text": "封面图片"
            # },
            {
                "type": "section",
                "text": {"type":"mrkdwn", "text": self.CoverUrl}
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'<{self.BestBitRateUrl}|点击查看视频>'
                }
            }
        ]
        return text, blocks
