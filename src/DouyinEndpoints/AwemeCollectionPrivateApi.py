from typing import Any, List, Dict
from unittest import TestCase, IsolatedAsyncioTestCase

from src.DouyinEndpoints.MyInfoEndpoint import MyInfoEndpoint
from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry, timestamp
from src.Services.DouyinScrapingSessionProvider import DouyinServicesInstance
from ..StudioY.DouyinSession import DouyinSession
from src.config.AppConfig import create_test_core_params, TestUserId
from src.extract import Extractor


class AwemeCollectionRequest:
    ...
    sec_user_id: str
    cursor: str

    def fill_api_params(self, params):
        params["sec_user_id"] = self.sec_user_id
        params["cursor"] = self.cursor

    def __init__(self, sec_user_id: str = None, cursor: str = None):
        self.sec_user_id = sec_user_id
        self.cursor = cursor


class AwemeCollectionResponse:
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
        result.aweme_list = obj.get("aweme_list") or []
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

    def __init__(self, session: DouyinSession):
        super().__init__(session)

    @retry
    def request(self, request: AwemeCollectionRequest) -> AwemeCollectionResponse:
        params = self.api_params.copy()
        request.fill_api_params(params)
        self.deal_url_params(params)
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
        return False
        return bool(aweme_list)

class AwemeCollection:
    __last_request: AwemeCollectionRequest | None
    __last_response: AwemeCollectionResponse | None
    __last_success_response: AwemeCollectionResponse | None
    __can_continue: bool
    __load_complete: bool

    __douyin_session: DouyinSession

    def __init__(self, recipient: IAwemeCollectionRecipient = None, session: DouyinSession = None):
        self.recipient = recipient
        self.session = session
        self.api = AwemeCollectionPrivateApi(session)
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

def get_sample_aweme_list():
    api = AwemeCollectionPrivateApi(create_test_core_params())
    request = AwemeCollectionRequest(sec_user_id=TestUserId)
    response = api.request(request)
    return response.aweme_list

class TestAwemeCollectionPrivateApi(IsolatedAsyncioTestCase):

    def test_request(self):
        api = AwemeCollectionPrivateApi(create_test_core_params())
        request = AwemeCollectionRequest(sec_user_id=TestUserId)
        response = api.request(request)
        self.assertIsNotNone(response)

    async def test_list(self):
        collection = AwemeCollection(IAwemeCollectionRecipient())
        await collection.load_full_list()
        breakpoint()



class CollectionEndpoint(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/aweme/listcollection/"  # 收藏API
    params = {
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

    def __init__(self, params: DouyinSession, sec_user_id: str,
                 pages: int = None, ):
        super().__init__(params)
        self.pages = pages
        self.sec_user_id = bool(sec_user_id)
        self.info = MyInfoEndpoint(params, sec_user_id)

    def run(self):
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取账号收藏数据", total=None)
            while not self.finished and self.pages > 0:
                progress.update(task_id)
                self._get_account_data(finished=True)
                self.pages -= 1
        self._get_owner_data()
        return self.response

    @retry
    def _get_account_data(self):
        params = self.params.copy()
        self.deal_url_params(params)
        form = {
            "count": "30",
            "cursor": self.cursor,
        }
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    data=form,
                    method='post')):
            self.log.warning("获取账号收藏数据失败")
            return False
        try:
            self.cursor = data['cursor']
            self.move_list_to_response(data["aweme_list"])
            self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"账号收藏数据响应内容异常: {data}")
            self.finished = True
            return False

    def _get_owner_data(self):
        if not any(self.response):
            return
        if self.sec_user_id and (
                info := Extractor.get_user_info(
                    self.info.run())):
            self.response.append({"author": info})
        else:
            temp_data = timestamp()
            self.log.warning(
                f"owner_url 参数未设置 或者 获取账号数据失败，本次运行将临时使用 {temp_data} 作为账号昵称和 UID")
            temp_dict = {
                "author": {
                    "nickname": temp_data,
                    "uid": temp_data,
                }
            }
            self.response.append(temp_dict)


class TestCollectionEndpoint(TestCase):

    def test_run(self):
        CollectionEndpoint(create_test_core_params(), TestUserId).run()
