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
        account_code = 'DF3'
        cookie = '__ac_nonce=066aab2bd00ef78ba801d; __ac_signature=_02B4Z6wo00f017nNIfwAAIDBvmcUWZjtxie57SVAAIji89; ttwid=1%7Cl5h52p4n9z9ORlsCNVO82R9ZkgWCWq7y5_KwL3jBq8M%7C1722462909%7Caf1b7b72b8e88a4f655395fd5f7c0eac1bcacc2ab1466acec3511e21383f02b9; UIFID_TEMP=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae53275fad1c075a5f00dd42ce8d0ee835365e57b384a3e3a9d0c7efe63091cfc7dd7fb27b418c146a74bac7353a6418c033e; douyin.com; device_web_cpu_core=12; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A12%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; csrf_session_id=0c09746c356341951759e149548056db; strategyABtestKey=%221722462912.404%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; xgplayer_user_id=229343204416; s_v_web_id=verify_lzady1p8_tNcqaNf9_CSKs_4JDN_98Lg_92gKwA2N3MwY; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; passport_csrf_token=dae16fda76afaa065f3adf93d7569f9e; passport_csrf_token_default=dae16fda76afaa065f3adf93d7569f9e; fpk1=U2FsdGVkX19Iowp8zKniHcF3yXLtq8A4u1F5aDIdKNaK6XSjBD6qWXPOPtKWYo4PU7sSV6t4jBo2SAA+KzOMgA==; fpk2=5e705226acd7a97aa6ee95ab188632d6; biz_trace_id=9fc75a59; bd_ticket_guard_client_web_domain=2; xg_device_score=7.802204888412783; UIFID=3451f3290245f54d68444d1ea9b086549aa1429a8a34f8bce366bfaafc2ae5326ce25601516126842e7b886bc59cb1057ec9dfd99db574d0f7e2095ffcb80b5e944e75e21958a66292878fe13cd6e101be013fe4abe439dc9096dd9abd22e3b746bb25dadee183f60843ac6d05dfd4e41efdeb565727d4559cd4522214e379c0ee4a35fb89f2ef092e799f89c093c73678b74cf8f8293470da443d0cec4e39bb; d_ticket=c381679beffd4b90160bd4ea2831959c43fa1; passport_assist_user=Ck_uo4iiPy5TTz65JMqindBoOBqbfJK5yglqv610NRvaKkDVfxz5DHZWqnpZbNcqyE337y7j3o2LSuL-KIrY7HWjLG4_v5NhefPwAzq-4bTeGkoKPPlIrE41IsOeDFlaBAIa4JI1Esf_xnkuC9PfLvZ3aC6bQ76ULq7mZPATgPXRXWBaaGlq6Cxus8tcO2gKMRCclNgNGImv1lQgASIBA-FogaQ%3D; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; sso_uid_tt=c50e37b572db27b7f16fba62b1a3433d; sso_uid_tt_ss=c50e37b572db27b7f16fba62b1a3433d; toutiao_sso_user=5c33e966b2af3b164e4005174c18233e; toutiao_sso_user_ss=5c33e966b2af3b164e4005174c18233e; sid_ucp_sso_v1=1.0.0-KDA5ODU1MmFjMGNiODI4MGMyZjVjY2VlYmI5Nzk3YTM2NzAzYmY0OWYKIQjghpC95s3WAhD_5aq1BhjvMSAMMPn1ma8GOAZA9AdIBhoCaGwiIDVjMzNlOTY2YjJhZjNiMTY0ZTQwMDUxNzRjMTgyMzNl; ssid_ucp_sso_v1=1.0.0-KDA5ODU1MmFjMGNiODI4MGMyZjVjY2VlYmI5Nzk3YTM2NzAzYmY0OWYKIQjghpC95s3WAhD_5aq1BhjvMSAMMPn1ma8GOAZA9AdIBhoCaGwiIDVjMzNlOTY2YjJhZjNiMTY0ZTQwMDUxNzRjMTgyMzNl; passport_auth_status=56034f3906c832d782ff577e2b85c80d%2C; passport_auth_status_ss=56034f3906c832d782ff577e2b85c80d%2C; uid_tt=2a2a93e711c0541854a689f30298d44c; uid_tt_ss=2a2a93e711c0541854a689f30298d44c; sid_tt=919538009ee6e0a19c34d8b462bc2c16; sessionid=919538009ee6e0a19c34d8b462bc2c16; sessionid_ss=919538009ee6e0a19c34d8b462bc2c16; is_staff_user=false; passport_fe_beating_status=true; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=7bdbea78799636123034bc21a6647159; __security_server_data_status=1; sid_guard=919538009ee6e0a19c34d8b462bc2c16%7C1722462982%7C5183996%7CSun%2C+29-Sep-2024+21%3A56%3A18+GMT; sid_ucp_v1=1.0.0-KGEyYmMxMmM4OTBmOTFiMTA2YmQ5OTg0ZDE4MWUxZmZkMjBmZmFiZDAKGwjghpC95s3WAhCG5qq1BhjvMSAMOAZA9AdIBBoCbHEiIDkxOTUzODAwOWVlNmUwYTE5YzM0ZDhiNDYyYmMyYzE2; ssid_ucp_v1=1.0.0-KGEyYmMxMmM4OTBmOTFiMTA2YmQ5OTg0ZDE4MWUxZmZkMjBmZmFiZDAKGwjghpC95s3WAhCG5qq1BhjvMSAMOAZA9AdIBBoCbHEiIDkxOTUzODAwOWVlNmUwYTE5YzM0ZDhiNDYyYmMyYzE2; publish_badge_show_info=%220%2C0%2C0%2C1722462983763%22; odin_tt=16c5501276a3a020489540f8d553acd9e12c933745e15d24cc53cff33cd4569ec42673299ea6aa3dbac37d4da06328fc; download_guide=%222%2F20240731%2F0%22; pwa2=%220%7C0%7C1%7C0%22; home_can_add_dy_2_desktop=%221%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTTFEQ0JGbDRBVmJQenNFMXludndpQ1F6SysxM0cwOWY0dS9mREpvaVhvZmlNTWdLNWhPSk1sT1Q1b0RSTzBxK3RmY1RpOXExdWlrM2VMYXR1TCsxQWM9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; IsDouyinActive=true'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
