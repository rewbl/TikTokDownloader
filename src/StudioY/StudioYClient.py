from unittest import TestCase

import requests
import json


class StudioYClient:
    def __init__(self, base_url='https://localhost:44358/api/douyin-accounts'):
        self.base_url = base_url

    def get_cookie(self, account_id):
        response = requests.get(f'{self.base_url}/cookie', params={'accountId': account_id}, verify=False)
        return response.json()

    def set_cookie(self, account_id, cookie):
        response = requests.put(f'{self.base_url}/cookie', params={'accountId': account_id},
                                data=json.dumps(cookie), headers={'Content-Type': 'application/json'}, verify=False)
        return response.json()

    def get_account_id_by_short_code(self, short_code):
        response = requests.get(f'{self.base_url}/account-id', params={'shortCode': short_code}, verify=False)
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

    def get_pending_videos(self, account_id, start_minutes_offset):
        response = requests.get(f"{self.base_url}/bookmarks/pending-download?accountId={account_id}"
                                f"&includeDownloaded={'true'}&startMinutesOffset={start_minutes_offset}", verify=False)
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
        account_code = 'BL1'
        cookie = 'ttwid=1%7CRmoTKjAh8zhkjx5Ekz83XbWCupAk4vusO0Srvm7wTt0%7C1708143526%7Ce37ab5179825f02cd73b28aa81f391b0b6217f8e8a725df050750b97e9271bf9; passport_csrf_token=0211e92ee61e17d7956fff136aa9107e; passport_csrf_token_default=0211e92ee61e17d7956fff136aa9107e; bd_ticket_guard_client_web_domain=2; passport_assist_user=Cj-WVRIeur1PbJm-53IrOS28mkExF8WuVGmli4KB2JwhGxiUh0_NA3bODFX5ZdcWQDQdJcgvgOe1VpX1NF65czwaSgo828jOWNPDO0-x08Vg0QJE9934r3aA5YwL0HzBWQUIc4KrcJpMICJ-78vt3XzzyJLST4JiMPQW4wBKQtmjEOjLyQ0Yia_WVCABIgEDG2SG6Q%3D%3D; n_mh=ToxDUIP1EE3Cs1qx5eTeCuSc1F_HYF22_NWbPp3NqWA; sso_uid_tt=07a960999ce50f79b760e52302c8518b; sso_uid_tt_ss=07a960999ce50f79b760e52302c8518b; toutiao_sso_user=47421a38c9783f9052c426bcaeeaf6d5; toutiao_sso_user_ss=47421a38c9783f9052c426bcaeeaf6d5; passport_auth_status=32fc9ee92ca24e61fefbf16413a49563%2C; passport_auth_status_ss=32fc9ee92ca24e61fefbf16413a49563%2C; LOGIN_STATUS=1; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=4b82705c500898c0c8457a83e6c2a8b1; __security_server_data_status=1; store-region=de; store-region-src=uid; my_rd=2; s_v_web_id=verify_lthj1fjz_83813dcd_4eb4_bfae_edf3_66f5e384c61e; __ac_nonce=065f3f5350087029af0f1; __ac_signature=_02B4Z6wo00f01etbZggAAIDAd8DVxZHWZq3re2KAAB8nG1ku.5-kFjFSf9XuWGt0g2mvmYf-WM-rHTA4V4TqGAJp2L-g25e5xtujixHN-GBJxO8H223cHoRIdnCIvWVFwXXsmXJpeVx9Gcy544; douyin.com; xg_device_score=6.905294117647059; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; IsDouyinActive=true; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A150%7D%22; publish_badge_show_info=%220%2C0%2C0%2C1710486847638%22; strategyABtestKey=%221710486847.944%22; csrf_session_id=eaf6df03306bcef8249ac6ea537b2d82; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAJKIOm63UxSmQMRAyiM43eGYA3R3qR6-rtr4jtAA_iQo%2F1710572400000%2F0%2F1710486848164%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRWdQRXRORStkdVB1T0p2UkZLZ05MK3dURU02TWIvakxMa1dKU3lTS2poRHZoZkdHMVNSMi9wQzdLZXVBZEFrUFU2YnlrMVMxckJYeE5KWXBQUWRCb3c9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; passport_fe_beating_status=true; sid_ucp_sso_v1=1.0.0-KGVkOWFlNmRkMWE4MmQyYWUyYmE2OGQ1YTA5ODZjZjkxNDQyN2MxZTYKHgjj0KC48M0MEMHqz68GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDQ3NDIxYTM4Yzk3ODNmOTA1MmM0MjZiY2FlZWFmNmQ1; ssid_ucp_sso_v1=1.0.0-KGVkOWFlNmRkMWE4MmQyYWUyYmE2OGQ1YTA5ODZjZjkxNDQyN2MxZTYKHgjj0KC48M0MEMHqz68GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDQ3NDIxYTM4Yzk3ODNmOTA1MmM0MjZiY2FlZWFmNmQ1; sid_guard=5cf75a9a00a3131e321325639e2b4fd8%7C1710486849%7C5184000%7CTue%2C+14-May-2024+07%3A14%3A09+GMT; uid_tt=a99e46209af7f3a205f8846932a82f2a; uid_tt_ss=a99e46209af7f3a205f8846932a82f2a; sid_tt=5cf75a9a00a3131e321325639e2b4fd8; sessionid=5cf75a9a00a3131e321325639e2b4fd8; sessionid_ss=5cf75a9a00a3131e321325639e2b4fd8; sid_ucp_v1=1.0.0-KGFiY2Q2ZjRkZWFmNGE5NDI3OGFlYTNhMGQ2NjUzNTc1NzdmM2I4MDQKGgjj0KC48M0MEMHqz68GGO8xIAw4BkD0B0gEGgJobCIgNWNmNzVhOWEwMGEzMTMxZTMyMTMyNTYzOWUyYjRmZDg; ssid_ucp_v1=1.0.0-KGFiY2Q2ZjRkZWFmNGE5NDI3OGFlYTNhMGQ2NjUzNTc1NzdmM2I4MDQKGgjj0KC48M0MEMHqz68GGO8xIAw4BkD0B0gEGgJobCIgNWNmNzVhOWEwMGEzMTMxZTMyMTMyNTYzOWUyYjRmZDg; msToken=NxSbnovPBEovgOtedE5cgj23VmE0HjkgV5bMxeXRpgR8HFHYOdqlAIgtJRG58ny-aV3tESuWkgA2GH2Q3EjhrnJsJrwFk56_AKcw8p0hxToCaMi2; odin_tt=5255e779c3b3386d4c453ed590e6b714534cf148b18aebabc4e2820a06d985eccfb56f41a0f7f41763b5821d7266e8bb5dde8903a0258b15635adbb75a48caa3; msToken=nTHNlvX4P9P1lBFV1_UqXEHIMM6bpofwHODmaIz87LAVfWhXfvIdzo7NtDQRG6OTy5269iT5EzE3rvz6ldIaBpBAksAv4imzsJu6evvGOs0gG7y_Nzx5ZWMSeA==; home_can_add_dy_2_desktop=%221%22'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
