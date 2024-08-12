import asyncio
import re
from datetime import datetime
from unittest import IsolatedAsyncioTestCase

import aiohttp


class DouyinFileDownloadServiceClient(object):

    async def download_file_remotely(self, server_url, video_url, local_dir):
        payload = {
            "url": video_url,
            "localDir": local_dir
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(server_url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        return False
        except Exception as e:
            return False

    async def download_file(self, video_url, nickname, remote_folder):
        server_url = "http://h8.9zma.com:8099/"
        time_str = datetime.now().strftime("%d %H_%M_%S")
        filename = f'{nickname[:40]}-{time_str}.mp4'
        filename = re.sub(r'[\\/*?:"<>|#\n\r]', '', filename)
        folder = remote_folder or "C:\\Users\\Admin\\Nox_share\\ImageShare\\监控\\"
        local_dir = f"{folder}{filename}"
        start = datetime.now()
        success = await self.download_file_remotely(server_url, video_url, local_dir)
        total_seconds = (datetime.now() - start).total_seconds()
        if success:
            print(f"Downloaded: {local_dir}, seconds: {total_seconds}")
        else:
            print(f"Failed to download: {local_dir}")

    def start_download_file(self, video_url, nickname, remote_folder=None):
        asyncio.create_task(self.download_file(video_url, nickname, remote_folder))

class TestDouyinFileDownloadServiceClient(IsolatedAsyncioTestCase):
    async def test(self):
        server_url='http://ha8d.9zma.com:8099/'
        localDir = 'C:\\Users\\Admin\\Nox_share\\ImageShare\\1.mp4'
        video_url='https://api-hl.amemv.com/aweme/v1/play/?video_id=v0d00fg10000cqkv6jvog65s0qrcb0m0&line=1&file_id=d24baa0efc194c65b7733eea4cbcf24e&sign=cd38c5d23949913249314650070c2de3&is_play_url=1&source=PackSourceEnum_PUBLISH'
        await DouyinFileDownloadServiceClient().download_file_remotely(server_url, video_url, localDir)

    def test_time(self):
        time_str = datetime.now().strftime("%d %H_%M_%S")
        print(time_str)