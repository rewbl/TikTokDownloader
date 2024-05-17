import asyncio
import os
import shutil
import time
from unittest.mock import Mock

import urllib3

from DouyinEndpoints.DiscoverPrivateApi import IDiscoversRecipient, load_existing_aweme_ids_from_database, Discovers
from DouyinEndpoints.FollowingPrivateApi import FollowListCandidates, FollowingList
from StudioY.DouyinSession import DouyinSession
from StudioY.StudioYClient import get_account_id_and_cookie
from app.BookmarkDownloader import async_bookmark, download_recent_videos
urllib3.disable_warnings()


async def main():
    cookie = 'ttwid=1%7C0VNEHBum2iXTl92HFD4vP6T54SgMMyEhySSjhuSjRGA%7C1715928882%7C9eb7d36da8e88a6dc1346de8f0884417ff4c3d0628c0c4e0f98c2afdd940caef; _waftokenid=eyJ2Ijp7ImEiOiJjd0xEV3djKzhiUkxlUlZmN0tmZWcrK211MjFpMHFpaUs5Mnl3VWJmM0w0PSIsImIiOjE3MTU5Mjg4ODIsImMiOiIvMHJ1aVpGTzAwS2lPdEhhdFE5aEEzemZLVDhXdGNRSlYxK09SZ1BZdlE0PSJ9LCJzIjoiOHQvZ1YvVENKUjhtM2xYZWRWaFlaTmU3WmpRdTJOZ3plZU5zL01FN1lHRT0ifQ; douyin.com; device_web_cpu_core=24; device_web_memory_size=8; architecture=amd64; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A24%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A0%7D%22; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; strategyABtestKey=%221715928885.749%22; s_v_web_id=verify_lwabr605_ddgY9kaL_JRCs_4VML_BFRs_RkWvllOwRRg3; csrf_session_id=1d90c9356ba786de489c4bfdbd06d713; passport_csrf_token=9221df11e34aac3740f316ea85b7dad7; passport_csrf_token_default=9221df11e34aac3740f316ea85b7dad7; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTy9sdmhMVkFGQVZxYlc5Mk14d3Y4ZlhFUjZsK2pWRStlYVRRY3FYK2ZxYm1XMjNBaU12NmpBVURzMXBpSDkzSzFtUFJmVXZhejlaSFEvQkVPdDJQVUk9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; bd_ticket_guard_client_web_domain=2; odin_tt=a54b47599c03ff174ae1facb9cfa8e314e20a4b10edd0f8e4e389645f07058529b40159fd2108808bfda8d79a0d5bad58ad9aa6262618671fdbd5025c22b5ddb0ac400e517ff2cdab5cebe1e1f355c19; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; msToken=_8RTsnkpfWO4wQ1DRU2kKZTe_yer0V2F0ICtYCUBbWIpXHOHoiXdF2xH-ENShMW0uMykRheI1Wi2ENVYvI5Kq2QCGRMDRtHg8xW7VtLdvvhdF3cpC9bSqQb_aAPqFMah'
    session = Mock()
    session.cookie= cookie
    recipient = IDiscoversRecipient()
    recipient.aweme_ids = await load_existing_aweme_ids_from_database()
    while True:
        discovers = Discovers(recipient, session)
        await discovers.load_full_list()

if __name__ == '__main__':

    asyncio.run(main())