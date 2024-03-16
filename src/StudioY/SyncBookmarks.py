from typing import List, Optional, Generic, TypeVar, Dict
from unittest import TestCase, IsolatedAsyncioTestCase

import requests
from pydantic import BaseModel

from src.DouyinEndpoints.AwemeCollectionPrivateApi import  AwemeCollection
from src.StudioY.DouyinSession import DouyinSession

CurrentDouyinAccountShortCode='BH1'
CurrentDouyinAccountId = ''

CurrentDouyinSession = DouyinSession(CurrentDouyinAccountShortCode)

class DouyinAuthorDto(BaseModel):
    Uid: Optional[str] = None
    SecUid: Optional[str] = None
    AvatarUrl: Optional[str] = None
    AvatarThumbUrl: Optional[str] = None
    Nickname: Optional[str] = None


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
    json = response.json() if response.status_code == 200 else None
    result.IsSuccess = response.status_code == 200 and json['isSuccess']
    result.Message = json['message']
    result.Code = json['code']
    result.Data = json['data']

    return result

class AwemeCollectionRecipient:
    def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:

        if not aweme_list:
            breakpoint()

        input = []
        for aweme in aweme_list or []:
            try:
                dto = create_video_dto(aweme)
                input.append(dto)
            except Exception as e:
                print(e)

        result = sync_bookmark(CurrentDouyinAccountId, input[::-1])
        if not result.IsSuccess:
            breakpoint()

        dded_total = result.Data['addedTotal']
        updated_total = result.Data['updatedTotal']
        print(f"Added {dded_total} and updated {updated_total} bookmarks")
        return bool(dded_total)

class TestSyncBookmarks2(IsolatedAsyncioTestCase):
    async def test_sync_bookmark(self):
        global CurrentDouyinSession, CurrentDouyinAccountId
        CurrentDouyinSession.load_session()
        CurrentDouyinAccountId = CurrentDouyinSession.account_id
        collection = AwemeCollection(AwemeCollectionRecipient(), CurrentDouyinSession)
        await collection.load_full_list()
        breakpoint()

def create_author_dto(author) -> DouyinAuthorDto:
    return DouyinAuthorDto(
        Uid=author['uid'],
        SecUid=author['sec_uid'],
        Nickname=author['nickname'],
        AvatarUrl=author.get('avatar_larger', {}).get('url_list', [None])[0],
        AvatarThumbUrl=author.get('avatar_thumb', {}).get('url_list', [None])[0]
    )


def create_video_dto(aweme) -> FavoriteVideoDto:
    cover_urls = aweme.get('video', {}).get('cover', {}).get('url_list', [])
    return FavoriteVideoDto(
        Author=create_author_dto(aweme.get('author', {})),
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

