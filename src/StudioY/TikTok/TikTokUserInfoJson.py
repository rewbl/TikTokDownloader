from pydantic import BaseModel


class TikTokUserInfoJson(BaseModel):
    avatar_larger_url: str
    avatar_thumb_url: str
    aweme_count: int
    follower_count: int
    following_count: int
    is_private_account: int
    nickname: str
    sec_uid: str
    total_favorited: int
    uid: str

    @staticmethod
    def from_json(json):
        avatar_larger_url, avatar_thumb_url = '', ''
        try:
            avatar_larger_url = json['avatar_larger']['url_list'][0]
        except:
            ...

        try:
            avatar_thumb_url = json['avatar_thumb']['url_list'][0]
        except:
            ...

        return TikTokUserInfoJson(
            avatar_larger_url=avatar_larger_url,
            avatar_thumb_url=avatar_thumb_url,
            aweme_count=json['aweme_count'],
            follower_count=json['follower_count'],
            following_count=json['following_count'],
            is_private_account=json['is_private_account'],
            nickname=json['nickname'],
            sec_uid=json['sec_uid'],
            total_favorited=json['total_favorited'],
            uid=json['uid']
        )
