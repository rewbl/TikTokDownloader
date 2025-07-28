import asyncio
import time
from datetime import datetime

import pytz

from DouyinEndpoints.Posts.UserPostPrivateApi import UserPostPrivateApi
from DouyinEndpoints.Posts.UserPostRequest import UserPostRequest
from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos
from FileDownload.DouyinFileDownloadServiceClient import DouyinFileDownloadServiceClient
from Slack.SlackDouyinMonitor import send_slack_notification
from StudioY.FavoriteVideoDto import FavoriteVideoDto


def is_skip_time():
    return False
    # Define the timezones for California and Beijing
    california_tz = pytz.timezone('America/Los_Angeles')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # Get the current time in both California and Beijing timezones
    california_time = datetime.now(california_tz).time()
    beijing_time = datetime.now(beijing_tz).time()

    # Check if it's skip time in California (10 PM to 7 AM)
    if california_time >= datetime.strptime("22:00", "%H:%M").time() or california_time < datetime.strptime("07:00",
                                                                                                            "%H:%M").time():
        return True

    # Check if it's skip time in Beijing (2 AM to 7 AM)
    if datetime.strptime("02:00", "%H:%M").time() <= beijing_time < datetime.strptime("07:00",
                                                                                      "%H:%M").time():
        return True

    # Return False if neither condition is met
    return False


class SingleUserNewPostMonitor:
    user: UserPostVideos
    check_interval_seconds = 20
    api: UserPostPrivateApi

    def __init__(self, user: UserPostVideos):
        self.user = user
        self.api = UserPostPrivateApi('')

    async def check_forever(self):
        while True:
            if is_skip_time():
                await asyncio.sleep(60)
                continue

            start_time = time.time()
            try:
                await self.check()
            except Exception as e:
                print(e)
            finally:
                await asyncio.sleep(self.check_interval_seconds - (time.time() - start_time))

    async def check(self):
        start = datetime.now()
        video_list = await self.__get_video_list()
        total_ms = (datetime.now() - start).total_seconds() * 1000
        if not video_list:
            print(f'Failed to get new videos for {self.user.name}. request ms: {total_ms}')
            return

        video_count = len(video_list)

        new_videos = self.user.update(video_list)
        if not new_videos:
            print(f'Got {video_count} videos for {self.user.name}. request ms: {total_ms}')
            return

        print(f'Got {len(new_videos)} new videos out of {video_count} for {self.user.name}. request ms: {total_ms}')
        for video in new_videos:
            await self.notify_new_video(video)

    async def __get_video_list(self):
        request = UserPostRequest(sec_user_id=self.user.sec_user_id)
        response = await self.api.request_async(request)
        if not response.confirmed_success:
            return []

        video_count = len(response.video_list)
        if video_count > 3:
            return response.video_list

        max_cursor = response.raw_data.get('max_cursor')
        request = UserPostRequest(sec_user_id=self.user.sec_user_id, max_cursor=max_cursor)
        response = await self.api.request_async(request)
        if not response.confirmed_success:
            return []
        return response.video_list

    async def notify_new_video(self, video: FavoriteVideoDto):
        text, blocks = video.notification_summary()
        if await send_slack_notification('vivian', text, blocks):
            print(f'Notified new video: {text}')
        try:
            DouyinFileDownloadServiceClient()\
                .start_download_file(video.BestBitRateUrl, video.Author.Nickname, self.user.remote_video_folder)
        except Exception as e:
            print(e)
