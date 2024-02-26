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
        super().__init__(params)

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
            return {}
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
            "aweme_count": {"$gt": 50},
            "total_favorited": {"$gt": 100000},
            "follower_count": {"$gt": 10000},
            "following_count": {"$gt": 60}
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

    last_request: FollowingRequest | None
    last_response: FollowingResponse | None

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
        self.last_request = None
        self.last_response = None
        self.__load_complete = False
        self.__can_continue = True

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

    async def load_full_list(self):
        await self.__recover_status()
        if not self.start_time:
            self.start_time = int(time.time())

        while self.__can_continue and not self.__load_complete:
            await self.__load_next_page()

    def __update_can_continue(self):
        self.__can_continue = False

    async def __load_next_page(self):
        self.last_response = self.api.request(self.__next_page_request)

        if self.last_response.confirmed_success:
            await self.__process_success_response()
            await asyncio.sleep(10)

        else:
            self.__update_can_continue()
            await self.__process_failed_response()

    @property
    def __next_page_request(self):
        max_time = int(time.time()) if not self.next_max_time else self.next_max_time
        self.last_request = FollowingRequest(self.sec_user_id, max_time=max_time)
        return self.last_request

    async def __process_success_response(self):
        await self.__save_followings_users()
        await self.__save_following_relations()
        self.__update_list_status()
        await self.__save_current_status()

    async def __save_followings_users(self):
        await NewUserList(self.last_response.followings).save()

    async def __save_following_relations(self):
        await NewFollowingRelations(self.sec_user_id,
                                    self.last_response.sec_user_id_list,
                                    self.last_response.load_time,
                                    self.last_response.min_time,
                                    self.last_response.max_time) \
            .save()

    def __update_list_status(self):
        if not self.start_total:
            self.start_total = self.last_response.total
        self.last_total = self.last_response.total
        self.next_max_time = self.last_response.min_time

        if self.last_response.has_more:
            return

        self.__load_complete = True
        self.end_total = self.last_response.total

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
            }}

        await DouyinDb.following_lists.update_one(update_filter, update, upsert=True)

    async def __process_failed_response(self):
        if self.last_response.is_list_invisible:
            self.end_time = int(time.time())
            self.__load_complete = True
            self.start_total = 0
            self.end_total = 0
            await self.__save_current_status()
            return
        breakpoint()


class TestFollowingPrivateApi(TestCase):

    def test_run(self):
        request_data = FollowingRequest("MS4wLjABAAAA1UQPfSAIjQJrmd4da8hI8xhuqClJTqWgvcSp-euVG6kvcLTGQQaaTFUQQMOVOP1_")
        data = FollowingPrivateApi(create_test_core_params()).request(request_data)


class TestFollowingList(IsolatedAsyncioTestCase):

    async def test_run(self):
        private_user_id = 'MS4wLjABAAAAZIOW4vpZ2s8efg0W4SbBWciK7cQ4llVh0fRXARGbWhSzeFLekAP8qqGHOdAE0o7D'
        private_user_id = await FollowListCandidates.get_next()
        # following_list = FollowingList("MS4wLjABAAAA1UQPfSAIjQJrmd4da8hI8xhuqClJTqWgvcSp-euVG6kvcLTGQQaaTFUQQMOVOP1_")
        following_list = FollowingList(private_user_id)
        await following_list.load_full_list()
