import json
from typing import Any, List, Dict
from unittest import IsolatedAsyncioTestCase

import urllib3

from DouyinEndpoints.EndpointBase import EndpointBase, Encrypter
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


class DiscoverPrivateApi(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/module/feed/"
    api_params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        'module_id': '3003101',
        'count': '120'
    }

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

    def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:
        old_len = len(self.aweme_ids)
        self.aweme_ids.update([aweme['aweme_id'] for aweme in aweme_list])
        new_len = len(self.aweme_ids)
        new_percent = (new_len - old_len) / len(aweme_list) * 100 if aweme_list else 0
        print(f'{len(self.aweme_ids)}, {len(aweme_list)}, {new_percent}')
        return bool(aweme_list)


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
            self.__can_continue = self.recipient.on_aweme_collection(self.__last_response.aweme_list)

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
        discovers = Discovers(IDiscoversRecipient(), session)
        await discovers.load_full_list()
