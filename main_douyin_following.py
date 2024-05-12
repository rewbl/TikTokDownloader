import asyncio
import os
import shutil
import time

from DouyinEndpoints.FollowingPrivateApi import FollowListCandidates, FollowingList
from StudioY.StudioYClient import get_account_id_and_cookie
from app.BookmarkDownloader import async_bookmark, download_recent_videos


async def main():
    _, cookie = get_account_id_and_cookie('BL1')
    while True:
        private_user_id = await FollowListCandidates.get_next()
        following_list = FollowingList(private_user_id, cookie)
        await following_list.load_full_list()

if __name__ == '__main__':

    asyncio.run(main())