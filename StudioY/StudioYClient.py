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
        account_code = 'DF5'
        cookie = '__ac_nonce=066d5068500226f36c73; __ac_signature=_02B4Z6wo00f01pOubLwAAIDAlARZGhbmGLaTjmgAAMJKfa; ttwid=1%7CSOC0kyMqJ6BaWsiYBPYdEWyiOz1JkYa8xqONda92ydg%7C1725236869%7C870c68763b50a503b7464abb09bb30efba6243bb8016caa3322c061c26e43845; UIFID_TEMP=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae532f5c98b91365d4a9894e74279fafff312b7f7ba0dc42b51f8cda23ef639709b2abfc7dc47cd7fb845ea10de3dc7cf073ce181c59d36bc3126e29ce2a2b97110256d51d4a0e6bc9b3cb4473af25669e6f0; douyin.com; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; hevc_supported=true; dy_swidth=3840; dy_sheight=2160; strategyABtestKey=%221725236871.813%22; csrf_session_id=a80a0d5ee9e3211a81c726019c915fb7; fpk1=U2FsdGVkX1/EmpyEzVS8nHr9MWVf1abMzmUOyI2S6dMb/BPUQ53jK/K0cXisHd/l9NTeGqNGduVd9ZdV6hjjpw==; fpk2=5e705226acd7a97aa6ee95ab188632d6; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; passport_csrf_token=3017a6d260d63797a6bb576540015937; passport_csrf_token_default=3017a6d260d63797a6bb576540015937; s_v_web_id=verify_m0k9hncf_AOBVOfRx_uagc_4pDS_8IV5_xfoJ0jlb3Xu5; bd_ticket_guard_client_web_domain=2; passport_assist_user=CkuZqM3BFo48SHiV5bEfaWN7hcqPyVD9jCGKnYgMSOLB1FNKxLOHrKMNY1M4DEgiUpV5QMqLFKoIgb3_fX5acT8VpVbXBr9bP34X51YaSgo8aUa5oXNFKomJ7BIf7s975X1zgrARbTtWxkioejj8seW-Ncj-LuPZUJscKVwIetTG-SIjFcnLpCcrIUVuEN7_2g0Yia_WVCABIgEDZ-W12g%3D%3D; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sso_uid_tt=0f5a86b0a07638eba78f61fe4daa60e3; sso_uid_tt_ss=0f5a86b0a07638eba78f61fe4daa60e3; toutiao_sso_user=132e2175e3ff1c1875f027a3cb24c7e5; toutiao_sso_user_ss=132e2175e3ff1c1875f027a3cb24c7e5; sid_ucp_sso_v1=1.0.0-KGZjYTQ2ZTkwNDc3ZDg1N2RmYTAwMTQ4MGQxMzIwMDc4Y2E2NjBmZDUKIQico-DejMyRBxCejdS2BhjvMSAMMPX6srAGOAZA9AdIBhoCaGwiIDEzMmUyMTc1ZTNmZjFjMTg3NWYwMjdhM2NiMjRjN2U1; ssid_ucp_sso_v1=1.0.0-KGZjYTQ2ZTkwNDc3ZDg1N2RmYTAwMTQ4MGQxMzIwMDc4Y2E2NjBmZDUKIQico-DejMyRBxCejdS2BhjvMSAMMPX6srAGOAZA9AdIBhoCaGwiIDEzMmUyMTc1ZTNmZjFjMTg3NWYwMjdhM2NiMjRjN2U1; passport_auth_status=735c895d73fa6e8359a66c6370d1fcdb%2C; passport_auth_status_ss=735c895d73fa6e8359a66c6370d1fcdb%2C; uid_tt=4f6d6ce725f6f74a59307b4ec0e2924c; uid_tt_ss=4f6d6ce725f6f74a59307b4ec0e2924c; sid_tt=ddd07110993cd4a4cd756b1bb49a0880; sessionid=ddd07110993cd4a4cd756b1bb49a0880; sessionid_ss=ddd07110993cd4a4cd756b1bb49a0880; is_staff_user=false; UIFID=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae532f5c98b91365d4a9894e74279fafff312b7f7ba0dc42b51f8cda23ef639709b2a1a7a00e1fd724558f599603bb4d26538db3be911fbbe5bfc5bcda223b3bf6a6d70c645aef827e9ce7135ea6c9c0c1c9ee786b487304632375f35f9185e7c60cf17cabb578da9f4e01cad5b01dc4db0cd0cfd4efcf2c78962f4d9e1fd16fa6841f99b4ce03d307e3451f5880c9b39790a4465ce5c3536f94d7033c84cbc3f7e74; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=917da389c5cacce453383cf3d05e1354; __security_server_data_status=1; passport_fe_beating_status=true; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTjV5dVdPVkxhNTRXOGhyRkgybkk4elozUjBFUng5VlhwTU9jbjkrSTFCNHBkV3pBZUNCSW14bFFjaUJFYjgxTDA4S3NYWml1dUgweXdYM1JUK0g2RjA9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; home_can_add_dy_2_desktop=%221%22; sid_guard=ddd07110993cd4a4cd756b1bb49a0880%7C1725236900%7C5183997%7CFri%2C+01-Nov-2024+00%3A28%3A17+GMT; sid_ucp_v1=1.0.0-KGZhOTQxMjEyZWQxNDVmM2NlY2M2ZThmMjUxN2QxZDBjNDA5MjQ4OGMKGwico-DejMyRBxCkjdS2BhjvMSAMOAZA9AdIBBoCaGwiIGRkZDA3MTEwOTkzY2Q0YTRjZDc1NmIxYmI0OWEwODgw; ssid_ucp_v1=1.0.0-KGZhOTQxMjEyZWQxNDVmM2NlY2M2ZThmMjUxN2QxZDBjNDA5MjQ4OGMKGwico-DejMyRBxCkjdS2BhjvMSAMOAZA9AdIBBoCaGwiIGRkZDA3MTEwOTkzY2Q0YTRjZDc1NmIxYmI0OWEwODgw; publish_badge_show_info=%220%2C0%2C0%2C1725236901385%22; biz_trace_id=2230c3a8; store-region=us; store-region-src=uid; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; odin_tt=b9bb37a24b0e4aa8bd295196bda97f3d00445f79482eaf9fac79ef0f76adb685f9dc0efbb1c6485401aa8fdb7df8e0c8; xgplayer_device_id=85500563515; xgplayer_user_id=113402172972'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
