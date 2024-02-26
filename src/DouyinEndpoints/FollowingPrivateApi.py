from typing import Any
from unittest import TestCase

from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.config.AppConfig import create_test_core_params
from src.config.RuntimeParameters import RuntimeCoreParameters


class FollowingRequest:
    sec_user_id: str
    max_time: int
    min_time: int
    myself_user_id: str

    def __init__(self, sec_user_id: str, max_time: int = 0, min_time: int = 0, myself_user_id: str = None):
        self.sec_user_id = sec_user_id
        self.max_time = max_time
        self.min_time = min_time
        self.myself_user_id = myself_user_id

    def fill_api_params(self, params):
        params["sec_user_id"] = self.sec_user_id
        params["max_time"] = self.max_time
        params["min_time"] = self.min_time


class FollowingResponse:
    followings: list[dict]
    max_time: int
    min_time: int
    has_more: bool
    total: int

    raw_data: Any

    def __init__(self, followings: list[dict], max_time: int, min_time: int, has_more: bool, total: int):
        self.followings = followings
        self.max_time = max_time
        self.min_time = min_time
        self.has_more = has_more
        self.total = total

    @staticmethod
    def from_dict(obj: Any) -> 'FollowingResponse':
        assert isinstance(obj, dict)
        followings = obj.get("followings", [])
        max_time = obj.get("max_time")
        min_time = obj.get("min_time")
        has_more = obj.get("has_more")
        total = obj.get("total")
        result = FollowingResponse(followings, max_time, min_time, has_more, total)
        result.raw_data = obj
        return result


class FollowingPrivateApi(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/user/following/list/"
    api_params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        # "user_id": "4432880630250244",
        "sec_user_id": "MS4wLjABAAAA1UQPfSAIjQJrmd4da8hI8xhuqClJTqWgvcSp-euVG6kvcLTGQQaaTFUQQMOVOP1_",
        "offset": "0",
        "min_time": "0",
        "max_time": "1708922579",
        "count": "20",
        "source_type": "1",
        "gps_access": "0",
        "address_book_access": "0",
        "is_top": "1",
        "pc_client_type": "1",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "platform": "PC",
        "downlink": "10",
    }

    # rest of the class
    def __init__(self, params: RuntimeCoreParameters, request_data: FollowingRequest):
        super().__init__(params)
        self.__request_data = request_data

    def request(self):
        params = self.api_params.copy()
        self.__request_data.fill_api_params(params)
        self.deal_url_params(params)
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                )):
            self.log.warning("获取账号收藏数据失败")
            return {}
        data = FollowingResponse.from_dict(data)
        nicenames = [r['nickname'] for r in data.followings]
        return data


class TestFollowingPrivateApi(TestCase):

    def test_run(self):
        request_data = FollowingRequest("MS4wLjABAAAA1UQPfSAIjQJrmd4da8hI8xhuqClJTqWgvcSp-euVG6kvcLTGQQaaTFUQQMOVOP1_")
        data = FollowingPrivateApi(create_test_core_params(), request_data).request()
