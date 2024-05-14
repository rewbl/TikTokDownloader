import asyncio
import os
import shutil
import time

import urllib3

from DouyinEndpoints.DiscoverPrivateApi import IDiscoversRecipient, load_existing_aweme_ids_from_database, Discovers
from DouyinEndpoints.FollowingPrivateApi import FollowListCandidates, FollowingList
from StudioY.DouyinSession import DouyinSession
from StudioY.StudioYClient import get_account_id_and_cookie
from app.BookmarkDownloader import async_bookmark, download_recent_videos
urllib3.disable_warnings()


async def main():
    session = DouyinSession('DF1')
    session.load_session()
    recipient = IDiscoversRecipient()
    recipient.aweme_ids = await load_existing_aweme_ids_from_database()
    discovers = Discovers(recipient, session)
    await discovers.load_full_list()

if __name__ == '__main__':

    asyncio.run(main())