from typing import List, Optional, Generic, TypeVar
from unittest import TestCase

import requests
from pydantic import BaseModel

import requests

class DouyinAuthorDto(BaseModel):
    Uid: Optional[str]
    SecUid: Optional[str]
    AvatarUrl: Optional[str]
    AvatarThumbUrl: Optional[str]
    Nickname: Optional[str]


class FavoriteVideoDto(BaseModel):
    Author: Optional[DouyinAuthorDto]
    AwemeId: Optional[str]
    Caption: Optional[str]
    Description: Optional[str]
    Height: Optional[str]
    Width: Optional[str]
    CoverUrl: Optional[str]
    Ratio: Optional[str]
    BestBitRateUrl: Optional[str]


T = TypeVar('T')


class Result(Generic[T]):
    Data: Optional[T]
    IsSuccess: Optional[bool]
    Message: Optional[str]
    Code: Optional[str]


def sync_bookmark(accountId, input: List[FavoriteVideoDto]) -> Result:

    url = f"https://localhost:44358/api/bookmarks/sync?accountId={accountId}"

    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.post(url, headers=headers, json=[dto.model_dump() for dto in input], verify=False)

    # Prepare the result
    result = Result()
    result.Data = response.json() if response.status_code == 200 else None
    result.IsSuccess = response.status_code == 200
    result.Message = 'Success' if result.IsSuccess else 'Failure'
    result.Code = str(response.status_code)

    return result

favorite_video_dto1 = FavoriteVideoDto(
    Author=DouyinAuthorDto(
        Uid="123",
        SecUid="abc",
        AvatarUrl="http://example.com/avatar1.jpg",
        AvatarThumbUrl="http://example.com/avatar_thumb1.jpg",
        Nickname="Author1"
    ),
    AwemeId="aweme1",
    Caption="Caption1",
    Description="Description1",
    Height="720",
    Width="1280",
    CoverUrl="http://example.com/cover1.jpg",
    Ratio="16:9",
    BestBitRateUrl="http://example.com/best_bit_rate1.mp4"
)

favorite_video_dto2 = FavoriteVideoDto(
    Author=DouyinAuthorDto(
        Uid="456",
        SecUid="def",
        AvatarUrl="http://example.com/avatar2.jpg",
        AvatarThumbUrl="http://example.com/avatar_thumb2.jpg",
        Nickname="Author2"
    ),
    AwemeId="aweme2",
    Caption="Caption2",
    Description="Description2",
    Height="720",
    Width="1280",
    CoverUrl="http://example.com/cover2.jpg",
    Ratio="16:9",
    BestBitRateUrl="http://example.com/best_bit_rate2.mp4"
)


class TestSyncBookmarks(TestCase):
    def test_sync_bookmark(self):
        accountId = "67e1eceb-91ab-4ba7-b6e3-e9e9777bfa3a"
        input = [favorite_video_dto1, favorite_video_dto2]
        result = sync_bookmark(accountId, input)
        self.assertTrue(result.IsSuccess)
