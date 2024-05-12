from unittest import TestCase

import requests
import json


class StudioYClient:
    def __init__(self, base_url='https://eu1.tta.rewbl.us/api'):
    # def __init__(self, base_url='https://localhost:44358/api'):
        self.base_url = base_url

    def get_cookie(self, account_id):
        response = requests.get(f'{self.base_url}/douyin-accounts/cookie', params={'accountId': account_id}, verify=False)
        return response.json()

    def set_cookie(self, account_id, cookie):
        response = requests.put(f'{self.base_url}/douyin-accounts/cookie', params={'accountId': account_id},
                                data=json.dumps(cookie), headers={'Content-Type': 'application/json'}, verify=False)
        return response.json()

    def get_account_id_by_short_code(self, short_code):
        response = requests.get(f'{self.base_url}/douyin-accounts/account-id', params={'shortCode': short_code}, verify=False)
        return response.json()

    def download_video(self, url, file_name):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Referer": "https://www.douyin.com"
        }
        response = requests.get(url, stream=True, headers=headers, allow_redirects=True, verify=False)
        with open(file_name, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

    def get_pending_videos(self, account_id, start_minutes_offset, include_downloaded=False):
        response = requests.get(f"{self.base_url}/bookmarks/pending-download?accountId={account_id}"
                                f"&includeDownloaded={include_downloaded}&startMinutesOffset={start_minutes_offset}", verify=False)
        return response.json()

    def set_downloaded(self, account_id, video_id):
        response = requests.post(f"{self.base_url}/bookmarks/set-downloaded?accountId={account_id}",
                                 json=[video_id], verify=False)
        return response.json()


def get_account_id_and_cookie(short_code):
    client = StudioYClient()
    account_result = client.get_account_id_by_short_code(short_code)
    accountId = account_result['data']
    cookie = client.get_cookie(accountId)['data']
    return accountId, cookie


class TestStudioYClient(TestCase):
    def test_account_id_and_cookie(self):
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code('DF1')
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, 'your-cookie')
        cookie = client.get_cookie(accountId)['data']
        assert cookie == 'your-cookie'

    def test_set_cookie(self):
        account_code = 'DF4'
        cookie = 'ttwid=1%7CNruNc5tCBzp-b0rL5db1bdBXBsryG3pLU9efqZBnGYs%7C1712368932%7C45e9c1030a6e19d5ea925161285b119a35c916b90d359c64e1b4940a6dddf498; passport_csrf_token=85b113533c398bfe0dfd3ab094ae014a; passport_csrf_token_default=85b113533c398bfe0dfd3ab094ae014a; bd_ticket_guard_client_web_domain=2; s_v_web_id=verify_lungamom_WLDbA01S_VNn6_4fEq_8yYC_n4PNcBKWBKex; d_ticket=5fd4d5a8bb04bff4f618861ec66d8d36195a1; store-region=us; store-region-src=uid; _bd_ticket_crypt_doamin=2; __security_server_data_status=1; my_rd=2; __ac_signature=_02B4Z6wo00f01VkWeUAAAIDAxY3Kjl6jfRlZNn3AADBY08; passport_assist_user=CkGcXCn7b-MBBOFXQ2xw9kV-0Smb5cLzFOmeFs1wR6_aZ5NxqqUMwa8hgzuMfUeUlajNG9a8wNGfO_ajSLMiZiji5xpKCjwqQuEOGekLcQHTvxpESqJUj0L7N5Xul0QNDVazxWnERPN2C516KIbRP3R3vzd4fMYW66GHqtVNW16XkNsQ7vPNDRiJr9ZUIAEiAQM7nVBZ; n_mh=Bdbeto8B8DXIgXtXZG-7Vw3HWofM6NyG-v3Wgk1pL6s; sso_uid_tt=e364d079b0e2315279b8b6b346d057b8; sso_uid_tt_ss=e364d079b0e2315279b8b6b346d057b8; toutiao_sso_user=66682a0c5f5882cb624d5d1f4c9a641d; toutiao_sso_user_ss=66682a0c5f5882cb624d5d1f4c9a641d; LOGIN_STATUS=1; _bd_ticket_crypt_cookie=ba0da1c8e1984755a2dbda1ebeb0d249; sid_ucp_v1=1.0.0-KGRhMTYwYzkwYmY4YzQyZjcxNTFiMmIxMjFlYTA5NzllMWFjZTViN2YKGwi45bD9lY3UBRDQ7sKwBhjvMSAMOAZA9AdIBBoCbHEiIDk3OGZiMGZhYTIxNDQxYjBiYjVjNjY1YmExN2NiODcw; ssid_ucp_v1=1.0.0-KGRhMTYwYzkwYmY4YzQyZjcxNTFiMmIxMjFlYTA5NzllMWFjZTViN2YKGwi45bD9lY3UBRDQ7sKwBhjvMSAMOAZA9AdIBBoCbHEiIDk3OGZiMGZhYTIxNDQxYjBiYjVjNjY1YmExN2NiODcw; douyin.com; xg_device_score=7.573184849754272; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A200%7D%22; publish_badge_show_info=%220%2C0%2C0%2C1715358343565%22; strategyABtestKey=%221715358343.809%22; csrf_session_id=2bb0b3c37968f2865ad7f372c5ef58b2; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRkNjSkhCWGJYZFdEanM0NkNGU0ZkdUZpeFI0ZDU4dzFzS0RQbmNvVzhBQWJpd0o3bmZzeldnZDJOSFNMNVMya3JxQkt1SDd1NUlFTDFncXUwQmtEWWc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; passport_fe_beating_status=true; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAqEjgkoeyf8zRWWwwrmkt2tMYh7-vFzOjSBZMPTb1kAfHEn5k2wWdPdXmAkql0VXZ%2F1715410800000%2F0%2F1715358344607%2F0%22; sid_ucp_sso_v1=1.0.0-KGIzZjY0MTEwZTJjOWNjZGY5ZGNiZGI2ODFkMzQzYjMxNWFhNmI4N2UKHwi45bD9lY3UBRCIlfmxBhjvMSAMMOL614QGOAZA9AcaAmhsIiA2NjY4MmEwYzVmNTg4MmNiNjI0ZDVkMWY0YzlhNjQxZA; ssid_ucp_sso_v1=1.0.0-KGIzZjY0MTEwZTJjOWNjZGY5ZGNiZGI2ODFkMzQzYjMxNWFhNmI4N2UKHwi45bD9lY3UBRCIlfmxBhjvMSAMMOL614QGOAZA9AcaAmhsIiA2NjY4MmEwYzVmNTg4MmNiNjI0ZDVkMWY0YzlhNjQxZA; sid_guard=66682a0c5f5882cb624d5d1f4c9a641d%7C1715358344%7C5184001%7CTue%2C+09-Jul-2024+16%3A25%3A45+GMT; uid_tt=e364d079b0e2315279b8b6b346d057b8; uid_tt_ss=e364d079b0e2315279b8b6b346d057b8; sid_tt=66682a0c5f5882cb624d5d1f4c9a641d; sessionid=66682a0c5f5882cb624d5d1f4c9a641d; sessionid_ss=66682a0c5f5882cb624d5d1f4c9a641d; home_can_add_dy_2_desktop=%221%22; odin_tt=160704e72dd8a671d3617d4ef49f5e25d2754a1164e73e4bac3f73a8b4220f6bb445556edfe9e4dd70d7e7d84d12846dd59146ad82f5d4d3e6245a4d4433d14dc54daf24396501e5854d8ff6975001cd; download_guide=%221%2F20240510%2F0%22; pwa2=%220%7C0%7C1%7C0%22; IsDouyinActive=true; msToken=5l_tq_HaFgp7wBgNUsL7VL_Non2SBycEqsTr1xZxovaFCsN-2A8uuHjdlC4A1cBFQjzNSij3a-51lKoxbCTQRcu_UrGZnOHJLxboHMov2zZMGE0biCYP'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
