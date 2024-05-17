import asyncio
import json
import time
from typing import Any, List, Dict
from unittest import IsolatedAsyncioTestCase

import urllib3
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne

from DouyinEndpoints.EndpointBase import EndpointBase, Encrypter
from MainDouyinMongoDb import DouyinDb
from StudioY.DouyinSession import DouyinSession
from StudioY.StudioYClient import get_account_id_and_cookie

urllib3.disable_warnings()


class DiscoverRequest:
    ...

    def fill_api_params(self, params):
        ...


class DiscoverResponse:
    confirmed_success: bool
    raw_data: Any
    aweme_list: list[dict]
    has_more: int
    status_code: int

    def __init__(self, raw_data: Dict | None):
        self.raw_data = raw_data or {}
        self.status_code = raw_data.get('status_code')
        self.has_more = raw_data.get('has_more')
        self.cards = raw_data.get('cards')
        self.confirmed_success = self.status_code == 0 and self.has_more == 1 and self.cards
        if not self.confirmed_success:
            self.aweme_list = []
            return
        self.aweme_list = [json.loads(card['aweme']) for card in self.cards]
        ...


class NewDiscoveredAwemeList:
    def __init__(self, aweme_list):
        self.aweme_list: List[dict] = aweme_list or []

    async def save(self):
        if not self.aweme_list:
            return

        collection: AsyncIOMotorCollection = DouyinDb.douyin_discovers_raw
        operations = []
        for aweme in self.aweme_list:
            aweme['_update_time'] = int(time.time())
            operations.append(UpdateOne(
                {'_id': aweme['aweme_id']},
                {'$set': aweme},
                upsert=True
            ))
        await collection.bulk_write(operations)


class DiscoverPrivateApi(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/module/feed/"
    api_params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        'module_id': '3003101',
        'count': '120'
    }
    def __init__(self, cookie: str):
        proxy = {
            "http": "http://zengboling:Supers8*@bj.tc.9zma.com:2808",
        }
        super().__init__(cookie, proxy)

    def request(self, request: DiscoverRequest) -> DiscoverResponse:
        params = self.api_params.copy()
        request.fill_api_params(params)
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    method='get')):
            return DiscoverResponse({})
        return DiscoverResponse(data)


class IDiscoversRecipient:
    aweme_ids = set()

    async def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:
        new_aweme_list = [aweme for aweme in aweme_list if aweme['aweme_id'] not in self.aweme_ids]
        new_percent = len(new_aweme_list) / len(aweme_list) * 100 if aweme_list else 0
        new_percent_text = f'{new_percent:.2f}' if new_percent else '0'
        self.aweme_ids.update([aweme['aweme_id'] for aweme in aweme_list])
        new_discovered_aweme_list = NewDiscoveredAwemeList(new_aweme_list)
        await new_discovered_aweme_list.save()
        print(f'{len(self.aweme_ids)}, {len(aweme_list)}, {new_percent_text}')
        return True


async def load_existing_aweme_ids_from_database():
    collection: AsyncIOMotorCollection = DouyinDb.douyin_discovers_raw
    cursor = collection.find({}, {'_id': 1})
    aweme_ids = set()
    async for document in cursor:
        aweme_ids.add(document['_id'])
    return aweme_ids


class Discovers:
    __last_request: DiscoverRequest | None
    __last_response: DiscoverResponse | None
    __last_success_response: DiscoverResponse | None
    __can_continue: bool
    __load_complete: bool

    def __init__(self, recipient: IDiscoversRecipient = None, session: DouyinSession = None):
        self.recipient = recipient
        self.session = session
        self.api = DiscoverPrivateApi(session.cookie)
        self.__last_request = None
        self.__last_response = None
        self.__can_continue = True
        self.__load_complete = False
        self.__last_retry = 0
        self.__has_error = False

    async def load_full_list(self):
        while self.__can_continue and not self.__load_complete:
            await self.__load_next_page()

    async def __load_next_page(self):
        self.__last_response = self.api.request(self.__next_page_request)

        if self.__last_response.confirmed_success:
            await self.__process_success_response()
        else:
            await self.__process_failed_response()

    @property
    def __next_page_request(self) -> DiscoverRequest:
        self.__last_request = DiscoverRequest()
        return self.__last_request

    async def __process_success_response(self):
        self.__last_retry = 0
        self.__last_success_response = self.__last_response
        self.__load_complete = not self.__last_response.has_more

        if self.recipient:
            self.__can_continue = await self.recipient.on_aweme_collection(self.__last_response.aweme_list)
        if not self.__last_response.aweme_list:
            await asyncio.sleep(10)

    @property
    def __can_retry(self):
        return self.__last_retry < 3

    async def __process_failed_response(self):
        if not self.__can_retry:
            self.__can_continue = False
            self.__load_complete = True
            self.__has_error = True
            return
        self.__last_retry += 1


class TestDiscoverPrivateApi(IsolatedAsyncioTestCase):

    def test_request(self):
        accountId, cookie = get_account_id_and_cookie('DF1')

        api = DiscoverPrivateApi(cookie)
        request = DiscoverRequest()
        response = api.request(request)

        self.assertIsNotNone(response)

    async def test_run(self):
        session = DouyinSession('DF1')
        session.load_session()
        recipient = IDiscoversRecipient()
        recipient.aweme_ids = await load_existing_aweme_ids_from_database()
        discovers = Discovers(recipient, session)
        await discovers.load_full_list()
