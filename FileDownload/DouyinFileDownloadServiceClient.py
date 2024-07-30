import asyncio
import re
from datetime import datetime

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

    async def download_file(self, video_url, nickname):
        server_url = "http://h8.9zma.com:8099/"
        time_str = datetime.now().strftime("%H-%M-%S")
        filename = f'{nickname[:40]}-{time_str}.mp4'
        filename = re.sub(r'[\\/*?:"<>|#\n\r]', '', filename)
        folder = "C:\\Users\\Admin\\Nox_share\\ImageShare\\"
        local_dir = f"{folder}{filename}"
        start = datetime.now()
        success = await self.download_file_remotely(server_url, video_url, local_dir)
        total_seconds = (datetime.now() - start).total_seconds()
        if success:
            print(f"Downloaded: {local_dir}, seconds: {total_seconds}")
        else:
            print(f"Failed to download: {local_dir}")

    def start_download_file(self, video_url, nickname):
        asyncio.create_task(self.download_file(video_url, nickname))
