import asyncio
from typing import List

from DouyinEndpoints.Posts.UserPostPrivateApi import IUserPostsRecipient, UserPostPrivateApi
from DouyinEndpoints.Posts.UserPostRequest import UserPostRequest
from DouyinEndpoints.Posts.UserPostResponse import UserPostResponse
from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos


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
