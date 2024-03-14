import asyncio
from typing import Any, List
from unittest import TestCase, IsolatedAsyncioTestCase

from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.Database.MainDouyinMongoDb import DouyinDb
from src.Services.DouyinScrapingSessionProvider import DouyinServicesInstance
from src.config.AppConfig import create_test_core_params
from src.config.RuntimeParameters import RuntimeCoreParameters

import time
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import UpdateOne


class NewFollowingRelations:
    def __init__(self, follower_sec_user_id, following_sec_user_id_list, update_time, min_time, max_time):
        self.follower_sec_user_id = follower_sec_user_id
        self.following_sec_user_id_list = following_sec_user_id_list
        self.update_time = update_time
        self.min_time = min_time
        self.max_time = max_time

    async def save(self):
        collection: AsyncIOMotorCollection = DouyinDb.following_relations
        operations = []
        for following_sec_user_id in self.following_sec_user_id_list:
            document = {
                '_id': {'follower': self.follower_sec_user_id, 'following': following_sec_user_id},
                'update_time': self.update_time,
                'min_time': self.min_time,
                'max_time': self.max_time
            }
            operations.append(UpdateOne(
                {'_id': {'follower': self.follower_sec_user_id, 'following': following_sec_user_id}},
                {'$set': document},
                upsert=True
            ))
        await collection.bulk_write(operations)


class NewUserList:
    def __init__(self, user_list):
        self.user_list: List[dict] = user_list or []

    async def save(self):
        collection: AsyncIOMotorCollection = DouyinDb.douyin_users
        operations = []
        for user in self.user_list:
            user['_update_time'] = int(time.time())
            operations.append(UpdateOne(
                {'_id': user['sec_uid']},
                {'$set': user},
                upsert=True
            ))
        await collection.bulk_write(operations)


class FollowingRequest:
    sec_user_id: str
    max_time: int
    myself_user_id: str

    def __init__(self, sec_user_id: str, max_time: int = 0, myself_user_id: str = None):
        self.sec_user_id = sec_user_id
        self.max_time = max_time
        self.myself_user_id = myself_user_id

    def fill_api_params(self, params):
        params["sec_user_id"] = self.sec_user_id
        params["max_time"] = self.max_time


class FollowingResponse:
    confirmed_success: bool
    followings: list[dict]
    max_time: int
    min_time: int
    has_more: bool
    total: int
    load_time: int
    raw_data: Any

    def __init__(self, followings: list[dict], max_time: int, min_time: int, has_more: bool, total: int):
        self.followings = followings
        self.max_time = max_time
        self.min_time = min_time
        self.has_more = has_more
        self.total = total
        self.confirmed_success = False

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
        result.load_time = int(time.time())
        result.check_success()
        return result

    @property
    def is_list_invisible(self):
        return self.raw_data.get('status_code') == 2096

    @property
    def nickname_list(self):
        return [r['nickname'] for r in self.followings]

    @property
    def sec_user_id_list(self):
        return [r['sec_uid'] for r in self.followings]

    def check_success(self):
        if not self.total:
            return
        if not self.followings:
            return
        self.confirmed_success = True


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
    def __init__(self, params: RuntimeCoreParameters):
        cookie='__ac_nonce=065f242f300626128c9c5; __ac_signature=_02B4Z6wo00f01mr9LbgAAIDAi.3OuOhcJE5q3SkAAP9c85; ttwid=1%7Cy_Yif1WKgFl7mRyfgtHg0xZuvXFOFp_ze1GnjB8We4k%7C1710375670%7C660d83cae745477a21e88ef0d5b412cff75d00a5fdc464eac0fe7c62e22947dc; douyin.com; device_web_cpu_core=24; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; strategyABtestKey=%221710375677.549%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; csrf_session_id=b3f0a1a2049bc50dc08891ea42288bc4; xgplayer_user_id=455156790902; ttcid=ff122030a4b04aaa947e229fee147ba636; GlobalGuideTimes=%221710375689%7C1%22; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; passport_csrf_token=e4e3964f490d60fba25d91844a8525f3; passport_csrf_token_default=e4e3964f490d60fba25d91844a8525f3; bd_ticket_guard_client_web_domain=2; passport_assist_user=Cj8GFMtFgqBf-OBtJQvcovtOE_E4ICVjqS5WnLcTYh-hyR0ZxRK7DIec6QVba9MmxK4aGSJg_8YiBG9XGrWXlCoaSgo8To0amt1XlLYTx2FLFg6A2Aj4dmg3bLIj12PqE9y-7uFQylPxtPTm8fYXkL2kgFnxlIbSgonabT-gW1hdEPfvyw0Yia_WVCABIgEDQ9dKwg%3D%3D; n_mh=ToxDUIP1EE3Cs1qx5eTeCuSc1F_HYF22_NWbPp3NqWA; sso_uid_tt=183747c20dd1b6f51f7d21b83df1fa68; sso_uid_tt_ss=183747c20dd1b6f51f7d21b83df1fa68; toutiao_sso_user=4cde23f294bb80744499ecd2d41cba9c; toutiao_sso_user_ss=4cde23f294bb80744499ecd2d41cba9c; sid_ucp_sso_v1=1.0.0-KDI4OWViMGNjNGU4ZmM0NjBlODY5Y2UxMmQxZTc4ZDkzNjU4YzIwZGMKHgjj0KC48M0MEK-Gya8GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDRjZGUyM2YyOTRiYjgwNzQ0NDk5ZWNkMmQ0MWNiYTlj; ssid_ucp_sso_v1=1.0.0-KDI4OWViMGNjNGU4ZmM0NjBlODY5Y2UxMmQxZTc4ZDkzNjU4YzIwZGMKHgjj0KC48M0MEK-Gya8GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDRjZGUyM2YyOTRiYjgwNzQ0NDk5ZWNkMmQ0MWNiYTlj; passport_auth_status=dd6345e80bf53c09f0dfd5e1fe8955f9%2C; passport_auth_status_ss=dd6345e80bf53c09f0dfd5e1fe8955f9%2C; uid_tt=ad1eebeae99839d811bbd16bdea37b87; uid_tt_ss=ad1eebeae99839d811bbd16bdea37b87; sid_tt=080d3a22a620fa47c895224a95c02174; sessionid=080d3a22a620fa47c895224a95c02174; sessionid_ss=080d3a22a620fa47c895224a95c02174; LOGIN_STATUS=1; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=1dcec6c252fa84065b05ede8b2e2bee9; __security_server_data_status=1; store-region=de; store-region-src=uid; publish_badge_show_info=%220%2C0%2C0%2C1710375733070%22; sid_guard=080d3a22a620fa47c895224a95c02174%7C1710375734%7C5183996%7CMon%2C+13-May-2024+00%3A22%3A10+GMT; sid_ucp_v1=1.0.0-KGJmNmI0YzcyMzc5Njk1YzgwMDQxYjY2MTc0NmU1ZjhmMTBlZTljZjkKGgjj0KC48M0MELaGya8GGO8xIAw4BkD0B0gEGgJscSIgMDgwZDNhMjJhNjIwZmE0N2M4OTUyMjRhOTVjMDIxNzQ; ssid_ucp_v1=1.0.0-KGJmNmI0YzcyMzc5Njk1YzgwMDQxYjY2MTc0NmU1ZjhmMTBlZTljZjkKGgjj0KC48M0MELaGya8GGO8xIAw4BkD0B0gEGgJscSIgMDgwZDNhMjJhNjIwZmE0N2M4OTUyMjRhOTVjMDIxNzQ; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAJKIOm63UxSmQMRAyiM43eGYA3R3qR6-rtr4jtAA_iQo%2F1710399600000%2F0%2F1710375733657%2F0%22; s_v_web_id=verify_ltqhk02x_hNmWiPQ5_j8kq_4VLH_ABC8_mGojKNsFxQwc; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; download_guide=%220%2F%2F1%22; xg_device_score=7.243616653118665; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAJKIOm63UxSmQMRAyiM43eGYA3R3qR6-rtr4jtAA_iQo%2F1710399600000%2F0%2F1710375909745%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTjVZSXZqS3BuL2xNV1BzTTc5bmtUV291U0lEeDJzUklYa3U0WWNXdVI5OVE5SnhibEpBNnBUOU56TVROaVRKa1ZJTWlDVUNXZDJ1a216cmloaEFLQWc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; tt_scid=OmM6.Efvt6wqFak7KXUeaScd0ftr5nit4fozhuNpUwEq8CHAyPE5hE.BFLPvQUJ.bf01; pwa2=%220%7C0%7C2%7C0%22; odin_tt=2d2f95206d16a3c65fc2e62feb953f6fbdd15248780671423b2c6deade56de66be2ea3629db646d991409b7d44bef1a7663dffd5ec3303e74a507d38f3d6ddab; msToken=OzOcctJY3yB2LEUzqX9_-woya344hrKXX2tlOuK4SDhB28dOY3u3NvdZKbztTsfRglRmfZIFtfgv0H4Ct9bqY_obCWzTxaFUiDl_t-KTo-BLky1yeIAMX08h97b8zNo=; msToken=NaV4Nj5uxdJqPnqO6xXRjhln0UBgrHOWQbCuUz49eIZ_-4RHnAyHQG9jGEgj4c9v9W2FdfxXc8wDs6_vQMOoyd_3GSjx9Nz02J8L_3dIvAKMlmw24ZZ2SaSoY2VWej8=; passport_fe_beating_status=false; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A24%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.25%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22'
        super().__init__(params, cookie=cookie)

    def request(self, request_data: FollowingRequest) -> FollowingResponse:
        params = self.api_params.copy()
        request_data.fill_api_params(params)
        self.deal_url_params(params)
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                )):
            self.log.warning("获取账号收藏数据失败")
            return FollowingResponse.from_dict({})
        # nicenames = [r['nickname'] for r in data['followings']]

        return FollowingResponse.from_dict(data)


class FollowListCandidates:
    @staticmethod
    async def get_next():
        # Check the following_lists collection first
        following_lists_collection = DouyinDb.following_lists
        document = await following_lists_collection.find_one({"load_complete": False})
        if document is not None:
            return document['_id']

        # If no document was found in following_lists, check the douyin_follow_list_candidates collection
        candidates_collection = DouyinDb.douyin_follow_list_candidates
        query = {
            "aweme_count": {"$gt": 100},
            "total_favorited": {"$gt": 100*1000},
            "follower_count": {"$gt": 10*1000},
            "following_count": {"$gte": 200, "$lte": 400}  # updated this line
        }
        documents = await candidates_collection.find(query).sort("following_count", -1).limit(1).to_list(None)
        if documents:
            return documents[0]['_id']
        else:
            return None


class FollowingList:
    sec_user_id: str | None
    start_time: int | None
    end_time: int | None

    start_total: int | None
    end_total: int | None

    last_total: int | None
    next_max_time: int | None

    __last_request: FollowingRequest | None
    __last_response: FollowingResponse | None

    __can_continue: bool
    __load_complete: bool

    def __init__(self, sec_user_id: str):
        self.sec_user_id = sec_user_id
        self.session = DouyinServicesInstance.get_session()
        self.api = FollowingPrivateApi(self.session.get_core_params())
        self.start_time = None
        self.end_time = None
        self.start_total = None
        self.end_total = None
        self.last_total = None
        self.next_max_time = None
        self.__last_request = None
        self.__last_response = None
        self.__last_success_response = None
        self.__load_complete = False
        self.__can_continue = True
        self.__last_retry = 0
        self.__has_error = False

    async def __recover_status(self):
        status_document = await DouyinDb.following_lists.find_one({'_id': self.sec_user_id})
        if status_document is None:
            return
        self.start_time = status_document.get('start_time')
        self.end_time = status_document.get('end_time')
        self.start_total = status_document.get('start_total')
        self.end_total = status_document.get('end_total')
        self.last_total = status_document.get('last_total')
        self.next_max_time = status_document.get('next_max_time')
        self.__can_continue = status_document.get('can_continue')
        self.__load_complete = status_document.get('load_complete')
        self.__last_retry = status_document.get('last_retry')
        self.__has_error = status_document.get('has_error')

    async def load_full_list(self):
        await self.__recover_status()
        if not self.start_time:
            self.start_time = int(time.time())

        while self.__can_continue and not self.__load_complete:
            await self.__load_next_page()


    async def __load_next_page(self):
        self.__last_response = self.api.request(self.__next_page_request)

        if self.__last_response.confirmed_success:
            await self.__process_success_response()
            # await asyncio.sleep(3)

        else:
            await self.__process_failed_response()

    @property
    def __next_page_request(self):
        max_time = int(time.time()) if not self.next_max_time else self.next_max_time
        self.__last_request = FollowingRequest(self.sec_user_id, max_time=max_time)
        return self.__last_request

    async def __process_success_response(self):
        self.__last_retry = 0
        self.__last_success_response = self.__last_response

        await self.__save_followings_users()
        await self.__save_following_relations()
        self.__update_list_status_after_success()
        await self.__save_current_status()

    async def __save_followings_users(self):
        await NewUserList(self.__last_success_response.followings).save()

    async def __save_following_relations(self):
        await NewFollowingRelations(self.sec_user_id,
                                    self.__last_success_response.sec_user_id_list,
                                    self.__last_success_response.load_time,
                                    self.__last_success_response.min_time,
                                    self.__last_success_response.max_time) \
            .save()

    def __update_list_status_after_success(self):
        if not self.start_total:
            self.start_total = self.__last_success_response.total
        self.last_total = self.__last_success_response.total
        self.next_max_time = self.__last_success_response.min_time

        if self.__last_success_response.has_more:
            return

        self.__load_complete = True
        self.end_total = self.__last_success_response.total

    async def __save_current_status(self):
        update_filter = {'_id': self.sec_user_id}
        update = {'$set':
            {
                'start_time': self.start_time,
                'end_time': int(time.time()),
                'start_total': self.start_total,
                'end_total': self.end_total,
                'last_total': self.last_total,
                'next_max_time': self.next_max_time,
                'can_continue': self.__can_continue,
                'load_complete': self.__load_complete,
                'last_retry': self.__last_retry,
                'has_error': self.__has_error
            }}

        await DouyinDb.following_lists.update_one(update_filter, update, upsert=True)

    @property
    def __can_retry(self):
        return self.__last_retry < 3

    async def __process_failed_response(self):
        if self.__last_response.is_list_invisible:
            self.end_time = int(time.time())
            self.__load_complete = True
            self.start_total = 0
            self.end_total = 0
            await self.__save_current_status()
            return

        if not self.__can_retry:
            self.__can_continue = False
            self.__load_complete = True
            self.__has_error = True
            await self.__save_current_status()
            # breakpoint()
            return

        self.__last_retry += 1



class TestFollowingPrivateApi(TestCase):

    def test_run(self):
        request_data = FollowingRequest("MS4wLjABAAAA1UQPfSAIjQJrmd4da8hI8xhuqClJTqWgvcSp-euVG6kvcLTGQQaaTFUQQMOVOP1_")
        data = FollowingPrivateApi(create_test_core_params()).request(request_data)


class TestFollowingList(IsolatedAsyncioTestCase):

    async def test_run(self):
        while True:
            private_user_id = await FollowListCandidates.get_next()
            following_list = FollowingList(private_user_id)
            await following_list.load_full_list()
