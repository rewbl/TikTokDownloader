from typing import Any, Dict

from StudioY.FavoriteVideoDto import FavoriteVideoDto


class UserPostResponse:
    confirmed_success: bool
    raw_data: Any
    aweme_list: list[dict]
    has_more: int
    status_code: int

    def __init__(self, raw_data: Dict | None):
        self.raw_data = raw_data or {}
        self.status_code = raw_data.get('status_code')
        self.has_more = raw_data.get('has_more')
        self.aweme_list = raw_data.get('aweme_list', [])
        self.confirmed_success = self.status_code == 0 and self.has_more == 1 and self.aweme_list
        self.video_list = [FavoriteVideoDto.from_dict(video) for video in self.aweme_list]
        ...
