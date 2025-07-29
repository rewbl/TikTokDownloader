import asyncio
import time
from datetime import datetime
from typing import Optional, List

import pytz

from DouyinEndpoints.Posts.UserPostPrivateApi import UserPostPrivateApi
from DouyinEndpoints.Posts.UserPostRequest import UserPostRequest
from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos
from StudioY.FavoriteVideoDto import FavoriteVideoDto
from NotionServices.async_task_processor import process_new_video
from NotionServices.douyin_post_service import NotionDouyinPostService


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
    account_page_id: Optional[str]
    existing_aweme_ids: set  # 内存中维护的已有视频ID集合

    def __init__(self, user: UserPostVideos, account_page_id: Optional[str] = None):
        self.user = user
        self.api = UserPostPrivateApi('')
        self.account_page_id = account_page_id
        self.post_service = NotionDouyinPostService() if account_page_id else None
        self.existing_aweme_ids = set()  # 初始化为空集合
        self._initialized = False  # 标记是否已初始化

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
        # 第一次运行时初始化已有视频ID列表
        if not self._initialized:
            await self._initialize_existing_videos()
            self._initialized = True

        start = datetime.now()
        video_list = await self.__get_video_list()
        total_ms = (datetime.now() - start).total_seconds() * 1000
        if not video_list:
            print(f'Failed to get new videos for {self.user.name}. request ms: {total_ms}')
            return

        video_count = len(video_list)

        # 使用内存中的ID列表检测新视频
        new_videos = self._detect_new_videos_in_memory(video_list)
        if not new_videos:
            print(f'Got {video_count} videos for {self.user.name}. request ms: {total_ms}')
            return

        print(f'Got {len(new_videos)} new videos out of {video_count} for {self.user.name}. request ms: {total_ms}')
        for video in new_videos:
            await self.notify_new_video(video)
            # 处理成功后，将视频ID添加到内存列表中
            self.existing_aweme_ids.add(video.AwemeId)

    async def __get_video_list(self):
        # 第一次请求：使用当前时间戳获取最新视频
        request = UserPostRequest(sec_user_id=self.user.sec_user_id)
        response = await self.api.request_async(request)
        if not response.confirmed_success:
            return []

        video_count = len(response.video_list)
        if video_count > 4:
            return response.video_list

        request = UserPostRequest(sec_user_id=self.user.sec_user_id)
        response = await self.api.request_async(request)
        if not response.confirmed_success:
            return []
        return response.video_list

    async def notify_new_video(self, video: FavoriteVideoDto):
        """
        处理新视频通知
        直接启动一次性任务处理
        """
        if not self.account_page_id:
            print(f"账号 {self.user.name} 没有关联的Notion页面ID，跳过处理")
            return

        try:
            # 直接启动一次性任务处理新视频
            await process_new_video(
                video=video,
                account_page_id=self.account_page_id,
                account_name=self.user.name,
                slack_channel='vivian'
            )
            print(f'已处理新视频: {video.AwemeId}')
        except Exception as e:
            print(f"处理新视频失败: {e}")

    async def _initialize_existing_videos(self):
        """
        初始化已有视频ID列表（只在第一次运行时执行）
        从Notion数据库加载该账号的所有已有视频ID
        """
        if not self.post_service or not self.account_page_id:
            print(f"账号 {self.user.name} 没有Notion配置，跳过初始化")
            return

        try:
            print(f"正在初始化账号 {self.user.name} 的已有视频列表...")
            self.existing_aweme_ids = self.post_service.get_existing_aweme_ids_for_account(self.account_page_id)
            print(f"账号 {self.user.name} 已有 {len(self.existing_aweme_ids)} 个视频记录")
        except Exception as e:
            print(f"初始化账号 {self.user.name} 的视频列表失败: {e}")
            self.existing_aweme_ids = set()

    def _detect_new_videos_in_memory(self, video_list) -> List[FavoriteVideoDto]:
        """
        使用内存中的ID列表检测新视频（快速）

        Args:
            video_list: 从抖音API获取的视频列表

        Returns:
            新视频列表
        """
        new_videos = []
        for video in video_list:
            if video.AwemeId not in self.existing_aweme_ids:
                new_videos.append(video)

        return new_videos

    async def _detect_new_videos_with_notion(self, video_list) -> List[FavoriteVideoDto]:
        """
        使用Notion数据库检测新视频

        Args:
            video_list: 从抖音API获取的视频列表

        Returns:
            新视频列表
        """
        if not self.post_service or not self.account_page_id:
            # 如果没有Notion服务，回退到原来的逻辑
            return self.user.update(video_list)

        try:
            # 获取该账号在Notion中已有的视频ID
            existing_aweme_ids = self.post_service.get_existing_aweme_ids_for_account(self.account_page_id)

            # 找出不在Notion中的新视频
            new_videos = []
            for video in video_list:
                if video.AwemeId not in existing_aweme_ids:
                    new_videos.append(video)

            return new_videos

        except Exception as e:
            print(f"使用Notion检测新视频失败: {e}")
            # 出错时回退到原来的逻辑
            return self.user.update(video_list)
