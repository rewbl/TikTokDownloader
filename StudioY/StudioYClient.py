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
        account_result = client.get_account_id_by_short_code('BH2')
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, 'your-cookie')
        cookie = client.get_cookie(accountId)['data']
        assert cookie == 'your-cookie'

    def test_set_cookie(self):
        account_code = 'DF4'
        cookie = '__ac_nonce=0668f40350010dc909325; __ac_signature=_02B4Z6wo00f01NfFbZwAAIDC0G9YOblX6HDX5WkAAFOD05; ttwid=1%7CZ-lz37ikf7B20RKJxecbs6fJwD4TgfOYR1fuWHBdY5g%7C1720664117%7C52daf2eee048f517fb4ec144e45202b14669cad0b4d26886e0c45d57360c8635; UIFID_TEMP=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae532f5c98b91365d4a9894e74279fafff312776284232f2e3ee1e645269b502c91f39be6451cd930d51dcf0f0734bd337b13e0095f0030c5113e146bc97c4540a24993b953f5ec57ef432906fd8e738a0a95; douyin.com; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; strategyABtestKey=%221720664119.934%22; xgplayer_user_id=583038693601; passport_csrf_token=b48e5d91f315e8d4f51c2a9ec3b5259c; passport_csrf_token_default=b48e5d91f315e8d4f51c2a9ec3b5259c; fpk1=U2FsdGVkX1+8QJjKsVvjRjigupP+/YSsNY9Q7xyD3WtY6Fny2sXXMlHzFdUcb9rectRDFFQ7fB0UgJ0jJPtWAg==; fpk2=5e705226acd7a97aa6ee95ab188632d6; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; csrf_session_id=7435d7639f1499dbe8d64bf139a2524f; s_v_web_id=verify_lygmznu5_fzQ6ZKfL_qH6X_4elP_ACXw_UiIyvf6i7Jxg; bd_ticket_guard_client_web_domain=2; xg_device_score=7.703735358684762; passport_assist_user=CkESWkT7AfhLpU6QbADIIf1gwcdUmH7_aOLoJ9-Ij8wCUeHBiLS0BCR5J_Hh_knw8qwi_BaqGdM-2MbWXUDIphiqAhpKCjz4suftmpiIk0zsVWQtN0ZHDt8bvHnoNXLFiUr6pkP-G1yljpC2oU2pY7VaZpqjaiEGSJde2MK5-1wYugYQw6rWDRiJr9ZUIAEiAQNJSwaW; n_mh=Bdbeto8B8DXIgXtXZG-7Vw3HWofM6NyG-v3Wgk1pL6s; sso_uid_tt=4542d3ab377a827a6675771281b2910e; sso_uid_tt_ss=4542d3ab377a827a6675771281b2910e; toutiao_sso_user=8aa6c12b997363b72834517eca3b771f; toutiao_sso_user_ss=8aa6c12b997363b72834517eca3b771f; sid_ucp_sso_v1=1.0.0-KDBkNjY2YzVkNTczMzRjNzVkMDk1NGI4Y2NjYmQ4ZmFhMzkwYjk4NGIKIQi45bD9lY3UBRDhgL20BhjvMSAMMOL614QGOAZA9AdIBhoCbGYiIDhhYTZjMTJiOTk3MzYzYjcyODM0NTE3ZWNhM2I3NzFm; ssid_ucp_sso_v1=1.0.0-KDBkNjY2YzVkNTczMzRjNzVkMDk1NGI4Y2NjYmQ4ZmFhMzkwYjk4NGIKIQi45bD9lY3UBRDhgL20BhjvMSAMMOL614QGOAZA9AdIBhoCbGYiIDhhYTZjMTJiOTk3MzYzYjcyODM0NTE3ZWNhM2I3NzFm; passport_auth_status=14c607df0acaafc51dfeeab8c19b3d5e%2C; passport_auth_status_ss=14c607df0acaafc51dfeeab8c19b3d5e%2C; uid_tt=5b69691802925cc1e98a07189407f447; uid_tt_ss=5b69691802925cc1e98a07189407f447; sid_tt=0457645901a8943989cacd286e3f528a; sessionid=0457645901a8943989cacd286e3f528a; sessionid_ss=0457645901a8943989cacd286e3f528a; UIFID=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae532f5c98b91365d4a9894e74279fafff312776284232f2e3ee1e645269b502c91f389dc3c234e59689d16e17bfa193124973e5e886df18908b0e45017ae729ed31559ecf8f182ab4a6231c7043a051596befdd84495671083359aac04c61dd1fa0919c1e1cd72be26e4c5d31168ba20f513533c293630c4350ebc2fdc94e35be3d4f432885939542c3d0d394205fc73454c21d06c47d721c51752b07a7043d374de; IsDouyinActive=true; publish_badge_show_info=%220%2C0%2C0%2C1720664166161%22; passport_fe_beating_status=true; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=54dcd68a659fd1b958e72413c9286482; __security_server_data_status=1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCUHdwUFBtdWpSSUs4cmhTVi9vN2NQTlE1d1RjVzFaUW5CWE1Ed3gxMG1QOWVmRjFRMkJCM09yTCtQemxSTmpuTDNxVTk5Z3FVYjRjTXpDVElMY0YyWVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; biz_trace_id=04dd4ba4; home_can_add_dy_2_desktop=%221%22; store-region=us; store-region-src=uid; odin_tt=cf68721bfc1c314a3358b6c899de97126c2858d6e1eb2fbb9da5a97225b54576099d46fd7bd98dc0c8c5e1af4ba578dc; download_guide=%221%2F20240710%2F0%22; d_ticket=ef28e4a0d2b8d3ef7a9b2bccb3d397af48fff; sid_guard=0457645901a8943989cacd286e3f528a%7C1720664635%7C5183530%7CMon%2C+09-Sep-2024+02%3A16%3A05+GMT; sid_ucp_v1=1.0.0-KDVjYzM3YTEwMGM2YTRhNjcyNTk1MjFhMmE2NDA5N2VlMjUxZDAxMzgKGwi45bD9lY3UBRC7hL20BhjvMSAMOAZA9AdIBBoCaGwiIDA0NTc2NDU5MDFhODk0Mzk4OWNhY2QyODZlM2Y1Mjhh; ssid_ucp_v1=1.0.0-KDVjYzM3YTEwMGM2YTRhNjcyNTk1MjFhMmE2NDA5N2VlMjUxZDAxMzgKGwi45bD9lY3UBRC7hL20BhjvMSAMOAZA9AdIBBoCaGwiIDA0NTc2NDU5MDFhODk0Mzk4OWNhY2QyODZlM2Y1Mjhh; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; my_rd=2; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAqEjgkoeyf8zRWWwwrmkt2tMYh7-vFzOjSBZMPTb1kAfHEn5k2wWdPdXmAkql0VXZ%2F1720681200000%2F0%2F0%2F1720665557034%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAqEjgkoeyf8zRWWwwrmkt2tMYh7-vFzOjSBZMPTb1kAfHEn5k2wWdPdXmAkql0VXZ%2F1720681200000%2F0%2F0%2F1720666157035%22'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
