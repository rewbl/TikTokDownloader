import asyncio
from unittest import IsolatedAsyncioTestCase

from PostMonitor.MonitorUsers import MonitorUsers
from PostMonitor.SingleUserNewPostMonitor import SingleUserNewPostMonitor
from DouyinEndpoints.Posts.UserPostVideos import UserPostVideos


class DouyinPostMonitor:
    def __init__(self):
        users = MonitorUsers('c:\\temp\\test\\DouyinUsers.xlsx').users
        self.monitors = [SingleUserNewPostMonitor(UserPostVideos(name, secUid, folder))
                         for name, secUid, folder in users]
        pass

    async def run(self):
        for monitor in self.monitors:
            asyncio.create_task(monitor.check_forever())
            await asyncio.sleep(0.1)
        while True:
            await asyncio.sleep(60)


class TestDouyinPostMonitor(IsolatedAsyncioTestCase):

    async def test_run(self):
        monitor = DouyinPostMonitor()
        await monitor.run()
