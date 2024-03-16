import asyncio
from typing import Any, List
from unittest import TestCase, IsolatedAsyncioTestCase

from src.DouyinEndpoints.EndpointBase import EndpointBase, Encrypter
from src.Infrastructure.Database.MainDouyinMongoDb import DouyinDb
from src.Services.DouyinScrapingSessionProvider import DouyinServicesInstance
from src.config.AppConfig import create_test_core_params

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
    def __init__(self):
        cookie='ttwid=1%7ChWHeTbIqkY8ccxTJ4SgrY6KxrytkmeOo2ZMkKsqb9FE%7C1706662275%7C5e8218e0ccdfb8f5fdb0bb57e28ea07527446c696d31faf82b57c1cf7b22b461; douyin.com; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; csrf_session_id=825bbee3fb626ec3eeaa6b77c1834e7d; passport_csrf_token=1aaa5c2935cde8fb44dbf1f6bc03529f; passport_csrf_token_default=1aaa5c2935cde8fb44dbf1f6bc03529f; bd_ticket_guard_client_web_domain=2; s_v_web_id=verify_lsbcdmy1_ABiSOfiJ_lpD2_4w2Y_9JCO_95bLi5YHy4oD; __ac_nonce=065f39d37008166efa1a9; __ac_signature=_02B4Z6wo00f01oAD7OAAAIDDHJhfL5q6l3qAI-hAAMX.Fof3YU1CAUg30L5sMQ40dHlh-pW7WnxSFP7bIRnSkorFKR.iXvb7Cs1si1BdeVTgQmZCzY6R.98WA4G6YIKH1.vda9aMO2PVHx8f68; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; strategyABtestKey=%221710464324.032%22; FORCE_LOGIN=%7B%22isForcePopClose%22%3A1%2C%22videoConsumedRemainSeconds%22%3A180%7D; my_rd=2; passport_assist_user=Cj9RHL9vlYiB33ioblSUBki_x9hZWadZOQkRfZT3h3VRH0ZZyYtW3T7HMWGPwZu8vOT4uhS1WonBsXgzlIO_cuoaSgo8aOkxSmvq-GKcMMJFlwgbPOScMXlHI8uZQ1nVZepvzncWAk7wrMH_VfNql30etCSdz_1DYzK-wDQz9P8eEL_7yw0Yia_WVCABIgEDJ5xwuA%3D%3D; n_mh=ToxDUIP1EE3Cs1qx5eTeCuSc1F_HYF22_NWbPp3NqWA; sso_uid_tt=1d76fcbce0941363979a79ddebed3c2e; sso_uid_tt_ss=1d76fcbce0941363979a79ddebed3c2e; toutiao_sso_user=851c9a07f8f99b4d7fc03dca736c4a55; toutiao_sso_user_ss=851c9a07f8f99b4d7fc03dca736c4a55; sid_ucp_sso_v1=1.0.0-KDhmZTExYTVkNTljOGFmYWJjMzM0NGYyNTc5MGQxMmYyYjA1NTMzMzkKHgjj0KC48M0MEJ27zq8GGO8xIAwwguLBpwY4BkD0BxoCbHEiIDg1MWM5YTA3ZjhmOTliNGQ3ZmMwM2RjYTczNmM0YTU1; ssid_ucp_sso_v1=1.0.0-KDhmZTExYTVkNTljOGFmYWJjMzM0NGYyNTc5MGQxMmYyYjA1NTMzMzkKHgjj0KC48M0MEJ27zq8GGO8xIAwwguLBpwY4BkD0BxoCbHEiIDg1MWM5YTA3ZjhmOTliNGQ3ZmMwM2RjYTczNmM0YTU1; passport_auth_status=ec5d92882df6201a52a9cf03232e00e2%2C; passport_auth_status_ss=ec5d92882df6201a52a9cf03232e00e2%2C; uid_tt=be2a16dcbeaadf6d5dc2a80273de2cc9; uid_tt_ss=be2a16dcbeaadf6d5dc2a80273de2cc9; sid_tt=224302418918382daf16f1dd2a7a16c1; sessionid=224302418918382daf16f1dd2a7a16c1; sessionid_ss=224302418918382daf16f1dd2a7a16c1; LOGIN_STATUS=1; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=660736874ef54a5073a7e7081c800ab9; __security_server_data_status=1; store-region=de; store-region-src=uid; sid_guard=224302418918382daf16f1dd2a7a16c1%7C1710464420%7C5183996%7CTue%2C+14-May-2024+01%3A00%3A16+GMT; sid_ucp_v1=1.0.0-KDJhYjUyMzJhMzQzMDc1OTVhMjU0MWVjYzg2ZjVmN2E0OTI2YTVlYmMKGgjj0KC48M0MEKS7zq8GGO8xIAw4BkD0B0gEGgJscSIgMjI0MzAyNDE4OTE4MzgyZGFmMTZmMWRkMmE3YTE2YzE; ssid_ucp_v1=1.0.0-KDJhYjUyMzJhMzQzMDc1OTVhMjU0MWVjYzg2ZjVmN2E0OTI2YTVlYmMKGgjj0KC48M0MEKS7zq8GGO8xIAw4BkD0B0gEGgJscSIgMjI0MzAyNDE4OTE4MzgyZGFmMTZmMWRkMmE3YTE2YzE; publish_badge_show_info=%220%2C0%2C0%2C1710464422917%22; home_can_add_dy_2_desktop=%221%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTUpUMUF0cit1ayt5U0dWYlZYVlVoRW51RmdpUk1NbGxSbUJtSUZOa28yOTJpSkdzU084SitrcDEybmg0b0xsYSs3UWxSckdhTWRubjluRWFzc2JiNVk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; passport_fe_beating_status=true; msToken=BSJO3XvNh8FprXs9-AWq-i_QduFJ9-MFdHzdSAlhR_zldueH04NNCrCy_qLHA0OnFW886GYXop1kUdkQW1UwCQkPNkdVhkpqrSqVVGUcdWHKJ78-xVdasxKL5pPb; tt_scid=pppMK1-0kXstPcEGHmkk75P.hUjyRDqpwKqHwF08MkZAmzXL3iF-IcWQFsPqaN.Ud2b0; msToken=0leamNrc1IsTWsD9mqw8RutP-cKic3b4HQDsJ2G1M-ZwhEn4kXe1bltYIi9payWlICCsxTNFIltZzQN5YVyfFzd2F_ydEaYNXNN5Jb0e7UD2IKVQFL8VIUrlFgEH; odin_tt=76020aeebc1a3386e5a156b200a0a66003cbe599d35ce0793c6eca8a577e7b19be2dddcbf58a0efe2ffc468f0c0257796f88036d7cfdf4f318cde37ef543f664; download_guide=%223%2F20240314%2F0%22; pwa2=%220%7C0%7C3%7C0%22; IsDouyinActive=true'
        super().__init__(cookie=cookie)

    def request(self, request_data: FollowingRequest) -> FollowingResponse:
        params = self.api_params.copy()
        request_data.fill_api_params(params)
        Encrypter.encrypt_request(params, 'self._get_ms_token()', 8)

        # self.deal_url_params(params)
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
        data = FollowingPrivateApi().request(request_data)
        self.assertEqual(len(data.nickname_list), 19)


class TestFollowingList(IsolatedAsyncioTestCase):

    async def test_run(self):
        while False:
            private_user_id = await FollowListCandidates.get_next()
            following_list = FollowingList(private_user_id)
            await following_list.load_full_list()
