from unittest import TestCase

import requests
import json


class StudioYClient:
    def __init__(self, base_url='https://eu1.tta.rewbl.us/api'):
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
        account_code = 'J3'
        cookie = '__ac_nonce=0661f4dbd00e0a8141886; _waftokenid=eyJ2Ijp7ImEiOiIxYUg0WDRVVTZpS1NHK05nMk50dVQ1NWw5Vm9zS0loMWgxNkcwZlkwdDRvPSIsImIiOjE3MTMzMjc1NDksImMiOiJaRk5LbjBxRmdpTXpGUG1jdDl6SVd4S2M3d0ZJSThzK3hpeVFBbm92dTdvPSJ9LCJzIjoibXU3KzdtQmJUUlg4WG4xei9KMFIwazdxTVRJdnZqSHJIQUtIeXlGREErZz0ifQ; __ac_signature=_02B4Z6wo00f01HO2G5gAAIDCkrb4msrVouRzlh8AAHr6fb; ttwid=1%7CUwm5AQc4NyEJQ4Hejip0Z3htCZFpXI51EppgvSJGz8g%7C1713327549%7C5a73624d77f7aa2c5757a91f8ff2a9aa9984eb5bbd750a76e05d7a1664f07c51; douyin.com; device_web_cpu_core=4; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A4%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; csrf_session_id=3034c3ece78495a4eb6a355c3592b7c2; strategyABtestKey=%221713327560.979%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Afalse%2C%22volume%22%3A0.5%7D; xgplayer_user_id=477104682270; passport_csrf_token=df92eecba6b6d828adf7a1427b706cd8; passport_csrf_token_default=df92eecba6b6d828adf7a1427b706cd8; bd_ticket_guard_client_web_domain=2; xg_device_score=7.008154088107373; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; download_guide=%221%2F20240417%2F0%22; pwa2=%220%7C0%7C1%7C0%22; s_v_web_id=verify_lv3b24oj_KQG14o7n_FtGm_4qaP_8CUy_WuFUxq3thrRI; d_ticket=35eb3f5357edc7698288ef2d7698ba3657f3c; passport_assist_user=CjwAHUNLruhnyC2A3T15efQbzfgK-7B-aQZbPocW-oiEwbovrqeXs0EPGKnWAakH-6h4cLUkJHOL4x2U72YaSgo8Cs7kyf4mR9aRsg35fqy-t_UAbd5qHW81NZoIzmKY9uFcd3Q5vz0Y9rtqzumme1rPLfDXwT2iAr8VBz0lELjvzg0Yia_WVCABIgED9p73HQ%3D%3D; n_mh=WxEkjpdQfBvzKmRpX0jDUaKutRNsRB-rHE9v6vu8tnI; sso_uid_tt=5ae885ba95ce38b6f9e523cc0f7812a8; sso_uid_tt_ss=5ae885ba95ce38b6f9e523cc0f7812a8; toutiao_sso_user=5b671ad34fb3cb5f266d4cdfe96c1d8c; toutiao_sso_user_ss=5b671ad34fb3cb5f266d4cdfe96c1d8c; sid_ucp_sso_v1=1.0.0-KGVlNDBiN2Y2MjU5ZGIwYTgxMjFmNjFlYzVhM2FjZjRlOTc3NzNhZTYKHQjOxKKe2wIQzZz9sAYY7zEgDDD9vJjUBTgGQPQHGgJscSIgNWI2NzFhZDM0ZmIzY2I1ZjI2NmQ0Y2RmZTk2YzFkOGM; ssid_ucp_sso_v1=1.0.0-KGVlNDBiN2Y2MjU5ZGIwYTgxMjFmNjFlYzVhM2FjZjRlOTc3NzNhZTYKHQjOxKKe2wIQzZz9sAYY7zEgDDD9vJjUBTgGQPQHGgJscSIgNWI2NzFhZDM0ZmIzY2I1ZjI2NmQ0Y2RmZTk2YzFkOGM; passport_auth_status=12d24e7ad99e6fdad3bc5130a4ad940b%2C; passport_auth_status_ss=12d24e7ad99e6fdad3bc5130a4ad940b%2C; uid_tt=3fcb79d675f8567f1369f580c89b5e2e; uid_tt_ss=3fcb79d675f8567f1369f580c89b5e2e; sid_tt=6002831b214b0267e10046a4e1074ed9; sessionid=6002831b214b0267e10046a4e1074ed9; sessionid_ss=6002831b214b0267e10046a4e1074ed9; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A0%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; LOGIN_STATUS=1; passport_fe_beating_status=true; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=a435e46ad408af09705d31d105625875; __security_server_data_status=1; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQmsrVWVKcFc3Unovb055cXJJaE9FZFNtOUVoN2VxMmR3S2tFTTJMOWR2Q0IxaUlvUUNGN2wvdjB2eGprUmpYeWtzMjZITm9ibTJmbitNT3o2VUdBdVE9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; store-region=de; store-region-src=uid; sid_guard=6002831b214b0267e10046a4e1074ed9%7C1713327702%7C5183994%7CSun%2C+16-Jun-2024+04%3A21%3A36+GMT; sid_ucp_v1=1.0.0-KDVmMjVkOGIxNGEwMzRmODhhMjNjZjViZmJmNGE2ZGNmZjJhMGFiMWYKGQjOxKKe2wIQ1pz9sAYY7zEgDDgGQPQHSAQaAmxmIiA2MDAyODMxYjIxNGIwMjY3ZTEwMDQ2YTRlMTA3NGVkOQ; ssid_ucp_v1=1.0.0-KDVmMjVkOGIxNGEwMzRmODhhMjNjZjViZmJmNGE2ZGNmZjJhMGFiMWYKGQjOxKKe2wIQ1pz9sAYY7zEgDDgGQPQHSAQaAmxmIiA2MDAyODMxYjIxNGIwMjY3ZTEwMDQ2YTRlMTA3NGVkOQ; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAMrvjaHYRAba46eapQ25N1pERhv1igxHBeWuBqQGNlSA%2F1713391200000%2F0%2F1713327706033%2F0%22; home_can_add_dy_2_desktop=%221%22; IsDouyinActive=true; publish_badge_show_info=%220%2C0%2C0%2C1713327710102%22; msToken=Etrql0JFjeh4G4XkdOk0_DNuMe6ZSRzXJJL7sydZ_DhhedB0G-a8zEkWv5IAqkx9O6BO6miy7a8DwY5yYqXqyn0xiHh_3BIJkqdnjMdm; odin_tt=9e4a854bcf7d136c8d291864244c61d8ff010b27a30e1be5a12b0e3415cb5383bb0c71cf10419022752308ad1b1a9bab'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
