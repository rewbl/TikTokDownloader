import asyncio
import time
from typing import List, Dict
from unittest import IsolatedAsyncioTestCase

import urllib3

from DouyinEndpoints.EndpointBase import EndpointBase
from DouyinEndpoints.Posts.UserPostRequest import UserPostRequest
from DouyinEndpoints.Posts.UserPostResponse import UserPostResponse
from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos
from StudioY.FavoriteVideoDto import FavoriteVideoDto

urllib3.disable_warnings()


class UserPostPrivateApi(EndpointBase):
    collection_api = "https://api.amemv.com/aweme/v1/aweme/post/"
    api_params = {
        "device_platform": "android",
        "aid": "2955",
        "channel": "carplay_xiaoai_2955",
        'sec_user_id': 'MS4wLjABAAAAJurvgyuY9p9WsHR69YSChOQvhVNEXvGKV_7BFO6zpWgttg2H2zLgnykIh3q6oVry',
        'count': '10',
        'max_cursor': '1737680701000',
        'ts': '1721199394',
        'app_type': 'lite',
        'os_api': '25',
        'device_type': 'PCRT00',
        'ssmix': 'a',
        'manifest_version_code': '9901504',
        'dpi': '240',
        'version_code': '9901504',
        'app_name': 'aweme',
        'version_name': '9.9.15',
        'device_id': '5827988420182290',
        'is_autoplay': 'true',
        'resolution': '720*1208',
        'os_version': '7.1.2',
        'language': 'zh',
        'device_brand': 'OPPO',
        'ac': 'wifi',
        'update_version_code': '9901504',
        'minor_status': '0',
        '_rticket': '1721199394273'
    }

    def __init__(self, cookie: str):
        proxy = {
            # "http": "http://zengboling:Supers8*@bj.tc.9zma.com:2808",
            "http": "http://107.173.30.188:2808",
        }
        proxy = {}
        super().__init__(cookie, proxy)

    def request(self, request: UserPostRequest) -> UserPostResponse:
        current_time = int(time.time())
        params = self.api_params.copy()
        request.fill_api_params(params, current_time)
        headers = {
            'User-Agent': 'okhttp/3.14.9',
            'X-Khronos': str(current_time),
        }
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    method='get',
                    proxy=self.proxy,
                    headers=headers)):
            return UserPostResponse({})
        return UserPostResponse(data)

    async def request_async(self, request: UserPostRequest) -> UserPostResponse:
        current_time = int(time.time())
        params = self.api_params.copy()
        request.fill_api_params(params, current_time)
        headers = {
            'User-Agent': 'okhttp/3.14.9',
            'X-Khronos': str(current_time),
        }
        async with Semaphore():
            if not (
                    data := await self.send_request_async(
                        self.collection_api,
                        params=params,
                        method='get',
                        headers=headers)):
                return UserPostResponse({})
            return UserPostResponse(data)


class Semaphore:
    _instance = None
    MAX = 30  # Maximum concurrency

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Semaphore, cls).__new__(cls)
            cls._instance._semaphore = asyncio.Semaphore(cls.MAX)
        return cls._instance

    async def __aenter__(self):
        await self._semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._semaphore.release()


class IUserPostsRecipient:
    users: Dict[str, UserPostVideos]

    def __init__(self):
        self.users = {}

    async def on_aweme_collection(self, sec_user_id, videos: List[FavoriteVideoDto]) -> bool:
        user_videos = self.users[sec_user_id]
        print(f'{len(videos)} videos')
        new_videos = user_videos.update(videos)
        if not new_videos:
            return True

        for video in new_videos:
            print(f'New video: {video.Caption}')
        return True


class TestUserPostPrivateApi(IsolatedAsyncioTestCase):

    async def test_request(self):
        cookie = "sid_guard=ded517612c83805ebbf388683f567493%7C1720686079%7C5183999%7CMon%2C+09-Sep-2024+08%3A21%3A18+GMT"
        secUid = "MS4wLjABAAAArwLl9tigxT8lVYgp1Hav-eZglxlLFFdHO7zOte_uNjk"
        api = UserPostPrivateApi('')
        request = UserPostRequest(secUid)
        response = await api.request_async(request)
        self.assertIsNotNone(response)

    async def test_run(self):
        cookie = "sid_guard=ded517612c83805ebbf388683f567493%7C1720686079%7C5183999%7CMon%2C+09-Sep-2024+08%3A21%3A18+GMT"
        secUid = "MS4wLjABAAAArwLl9tigxT8lVYgp1Hav-eZglxlLFFdHO7zOte_uNjk"
        users = [UserPostVideos("douyin1", secUid)]
        recipient = IUserPostsRecipient()
        recipient.users = {secUid: users[0]}
        userPosts = UserPosts(cookie, recipient, users)
        await userPosts.load_forever()



class UserPosts:
    __last_request: UserPostRequest | None
    __last_response: UserPostResponse | None
    __last_success_response: UserPostResponse | None
    __can_continue: bool
    __load_complete: bool

    users: List[UserPostVideos]

    def __init__(self, cookie: str, recipient: IUserPostsRecipient, users: List[UserPostVideos] = None):
        self.recipient = recipient
        self.users = users or []
        self.api = UserPostPrivateApi(cookie)
        self.__last_request = None
        self.__last_response = None
        self.__can_continue = True
        self.__load_complete = False
        self.__last_retry = 0
        self.__has_error = False

    async def load_forever(self):
        while self.__can_continue and not self.__load_complete:
            await self.__load_next_page()
            await asyncio.sleep(0.1)

    async def __load_next_page(self):
        self.__last_response = self.api.request(self.__next_page_request)

        if self.__last_response.confirmed_success:
            await self.__process_success_response()
        else:
            await self.__process_failed_response()

    @property
    def __next_page_request(self) -> UserPostRequest:
        user = self.users.pop(0)
        self.users.append(user)
        self.__last_request = UserPostRequest(sec_user_id=user.sec_user_id, name=user.name)
        return self.__last_request

    async def __process_success_response(self):
        self.__last_retry = 0
        self.__last_success_response = self.__last_response
        self.__load_complete = not self.__last_response.has_more

        if not self.recipient:
            return
        self.__can_continue = await self.recipient.on_aweme_collection(
            self.__last_request.sec_user_id, self.__last_response.video_list)

    @property
    def __can_retry(self):
        return self.__last_retry < 300000

    async def __process_failed_response(self):
        if not self.__can_retry:
            self.__can_continue = False
            self.__load_complete = True
            self.__has_error = True
            return
        self.__last_retry += 1
