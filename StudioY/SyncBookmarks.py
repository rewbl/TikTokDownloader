from typing import List, Optional, Generic, TypeVar, Dict
from unittest import IsolatedAsyncioTestCase

import requests
from pydantic import BaseModel

from DouyinEndpoints.AwemeCollectionPrivateApi import AwemeCollection
from StudioY.DouyinSession import DouyinSession


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


T = TypeVar('T')


class Result(Generic[T]):
    Data: Optional[T]
    IsSuccess: Optional[bool]
    Message: Optional[str]
    Code: Optional[str]


def sync_bookmark(accountId, input: List[FavoriteVideoDto]) -> Result:
    url = f"https://tta.rewbl.us/api/bookmarks/sync?accountId={accountId}"

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
    account_id: str = None
    no_added_page_total: int = 0
    max_no_added_page = 3

    def __init__(self, account_id: str = None):
        self.account_id = account_id
        self.no_added_page_total = 0

    def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:

        # if not aweme_list:
        #     breakpoint()

        input = []
        for aweme in aweme_list or []:
            try:
                dto = FavoriteVideoDto.from_dict(aweme)
                input.append(dto)
            except Exception as e:
                print(e)

        result = sync_bookmark(self.account_id, input[::-1])
        if not result.IsSuccess:
            breakpoint()

        added_total = result.Data['addedTotal']
        updated_total = result.Data['updatedTotal']
        print(f"Added {added_total} and updated {updated_total} bookmarks")

        self.no_added_page_total = 0 if added_total else self.no_added_page_total + 1
        has_any = bool(added_total + updated_total)
        can_have_more_no_added_pages = self.no_added_page_total < self.max_no_added_page
        can_continue = has_any and can_have_more_no_added_pages
        return can_continue


class TestSyncBookmarks2(IsolatedAsyncioTestCase):
    async def test_sync_bookmark(self):
        session = DouyinSession('DF1')
        session.load_session()
        collection = AwemeCollection(AwemeCollectionRecipient(session.account_id), session)
        await collection.load_full_list()
        breakpoint()