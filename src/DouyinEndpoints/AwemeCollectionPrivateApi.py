from typing import Any, List, Dict
from unittest import IsolatedAsyncioTestCase

from src.DouyinEndpoints.EndpointBase import EndpointBase, Encrypter
from src.StudioY.DouyinSession import DouyinSession
from src.StudioY.StudioYClient import get_account_id_and_cookie


class AwemeCollectionRequest:
    ...
    cursor: str

    def fill_api_params(self, params):
        params["cursor"] = self.cursor

    def __init__(self, cursor: str = None):
        self.cursor = cursor


class AwemeCollectionResponse:
    confirmed_success: bool
    cursor: str
    raw_data: Any
    aweme_list: list[dict]
    has_more: int
    status_code: int

    def __init__(self, cursor: str = None, raw_data: Any = None, aweme_list: list[dict] = None,
                 has_more: int = None, status_code: int = None):
        self.cursor = cursor
        self.raw_data = raw_data
        self.aweme_list = aweme_list or []
        self.has_more = has_more
        self.status_code = status_code
        self.confirm_success = False

    @staticmethod
    def from_dict(obj: Any) -> 'AwemeCollectionResponse':
        result = AwemeCollectionResponse()
        result.raw_data = obj
        result.cursor = obj.get("cursor")
        result.aweme_list = obj.get("aweme_list")
        result.has_more = obj.get("has_more")
        result.status_code = obj.get("status_code")
        return result

    @property
    def confirmed_success(self):
        return 'aweme_list' in self.raw_data and 'has_more' in self.raw_data


class AwemeCollectionPrivateApi(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/aweme/listcollection/"  # 收藏API
    api_params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "publish_video_strategy_type": "2",
        "pc_client_type": "1",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "platform": "PC",
        "downlink": "10",
    }


    def request(self, request: AwemeCollectionRequest) -> AwemeCollectionResponse:
        params = self.api_params.copy()
        request.fill_api_params(params)
        Encrypter.encrypt_request(params, 'msToken', 8)
        form = {
            "count": "30",
            "cursor": request.cursor,
        }
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    data=form,
                    method='post')):
            self.log.warning("获取账号收藏数据失败")
            return AwemeCollectionResponse.from_dict({})
        return AwemeCollectionResponse.from_dict(data)


class IAwemeCollectionRecipient:
    def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:
        return bool(aweme_list)


class AwemeCollection:
    __last_request: AwemeCollectionRequest | None
    __last_response: AwemeCollectionResponse | None
    __last_success_response: AwemeCollectionResponse | None
    __can_continue: bool
    __load_complete: bool

    def __init__(self, recipient: IAwemeCollectionRecipient = None, session: DouyinSession = None):
        self.recipient = recipient
        self.session = session
        self.api = AwemeCollectionPrivateApi(session.cookie)
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
    def __next_page_request(self) -> AwemeCollectionRequest:
        cursor = self.__last_response.cursor if self.__last_response else None
        self.__last_request = AwemeCollectionRequest(cursor=cursor)
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


class TestAwemeCollectionPrivateApi(IsolatedAsyncioTestCase):

    def test_request(self):
        accountId, cookie = get_account_id_and_cookie('DF1')

        api = AwemeCollectionPrivateApi(cookie)
        request = AwemeCollectionRequest()
        response = api.request(request)

        self.assertIsNotNone(response)
        self.assertEqual(len(response.aweme_list), 29)
