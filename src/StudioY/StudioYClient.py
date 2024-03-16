from unittest import TestCase

import requests
import json


class StudioYClient:
    def __init__(self, base_url='https://localhost:44358/api'):
        self.base_url = base_url

    def get_cookie(self, account_id):
        response = requests.get(f'{self.base_url}/douyin-accounts/cookie', params={'accountId': account_id}, verify=False)
        return response.json()

    def set_cookie(self, account_id, cookie):
        response = requests.put(f'{self.base_url}//douyin-accounts/cookie', params={'accountId': account_id},
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

    def get_pending_videos(self, account_id, start_minutes_offset):
        response = requests.get(f"{self.base_url}/bookmarks/pending-download?accountId={account_id}"
                                f"&includeDownloaded={'false'}&startMinutesOffset={start_minutes_offset}", verify=False)
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
        account_code = 'J1'
        cookie = 'store-region=cn-hn; d_ticket=be73d5c303cf7ba59baf6d77b3c6b3afeb119; my_rd=2; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; xgplayer_user_id=839818690335; store-region-src=uid; _bd_ticket_crypt_doamin=2; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; _bd_ticket_crypt_cookie=771cf1301b938695d7a1792f117caf92; LOGIN_STATUS=1; __security_server_data_status=1; ttwid=1%7C-7d2J6QheXNJBQHvTiAE6vkyaun4OLo_7Gjzq-TAmoo%7C1708143114%7C559ef741577955a187969771bf153b730d0bc77ce105ba69dfd689b7947283dc; passport_csrf_token=4c812de13cc1211e038f38ef0bdcf456; passport_csrf_token_default=4c812de13cc1211e038f38ef0bdcf456; bd_ticket_guard_client_web_domain=2; dy_swidth=3840; dy_sheight=2160; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; xgplayer_device_id=52703508981; passport_assist_user=CktOtIzfbFympTViuaxDAPHgyU7tFxdfLJ_IQ3WT_a1OiynX5kE7E7SzM4QODdXUObnkZD_a-I5Rw0m9bF1vtzRqnTHpAPAiAA88VpIaSgo8Bf29X3wt7H9-MutMriejP3PCKj1NLK8xVJPbrylb73u_m1yVztL5zL6oj9dD9Jzvb6vcRn2jBFY_WLIdEJauyw0Yia_WVCABIgEDK-uPbA%3D%3D; sso_uid_tt=c66172b292a4134ed66b0839f1128120; sso_uid_tt_ss=c66172b292a4134ed66b0839f1128120; toutiao_sso_user=57094aeeb3506c774dd250d7c93ad342; toutiao_sso_user_ss=57094aeeb3506c774dd250d7c93ad342; sid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; ssid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; passport_auth_status=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; passport_auth_status_ss=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; uid_tt=842dc94e71572b3e2c63d25db2115258; uid_tt_ss=842dc94e71572b3e2c63d25db2115258; sid_tt=660e6ee9becc05fd6ac177b6f3c91e20; sessionid=660e6ee9becc05fd6ac177b6f3c91e20; sessionid_ss=660e6ee9becc05fd6ac177b6f3c91e20; sid_guard=660e6ee9becc05fd6ac177b6f3c91e20%7C1709861492%7C5183998%7CTue%2C+07-May-2024+01%3A31%3A30+GMT; sid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; ssid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; publish_badge_show_info=%220%2C0%2C0%2C1710289638660%22; strategyABtestKey=%221710486710.035%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710572400000%2F0%2F1710527359125%2F0%22; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710572400000%2F0%2F1710531769491%2F0%22; tt_scid=fM.oupchdLNyOCYmfI0JRqHky53ll7bR.FFTijMhPIWZSreLNrdEBogXfIIXzuPkaacd; msToken=-W4MKYFDBieGgEtjSWe-EBfala9LSyeG6zoNDOCaczXpYqYNFw5tx8ziHSstF82UvPTSMy0vv0RiYEXrFgE7Cu6qzzTAICgyzF5VUSFnyAm08kkzt1bbAg==; odin_tt=f7dbf0f2cf7083c94130bcee99068002dab43140c356b232228a0c326804ff64775b6d1b8c8ea975f556929f6b095420; pwa2=%220%7C0%7C1%7C0%22; msToken=iFiWIUGty0CUIxZcxMEt1aSSM2pVX8BDwf194RxMmUl4TsE_R_tkPj6QHRz3Zt3LOMO2sRGxH2Lnvqn2jijbIw3QPrQi7PM9ezhIhHFw4-Xo3jJpmFIRpA==; __ac_nonce=065f4d24e00f0f6bcd761; __ac_signature=_02B4Z6wo00f01-LIaHgAAIDCflPbt3R5RWPi6GzAAJ1Qn9FBakIkn85pfGpwsWxPy.-P7.XOXdGpqBYVCDW9Ht94RE17xkYMisV7HvBLq6s9-wjnXXpKpYTy-fg1cXlYjBa83y.nq4wtRLJsfc; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.35%2C%5C%22effective_type%5C%22%3A%5C%223g%5C%22%2C%5C%22round_trip_time%5C%22%3A350%7D%22; csrf_session_id=eaf6df03306bcef8249ac6ea537b2d82; passport_fe_beating_status=true; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRUZMM0N1NGxtQWFUT2lPQWRCWHUvZnowVnUwRlNXNkdhRnYrM1dyMHYvN1AzcXZiN2dsakU1VHBjZjJuczcvVUd0NER5a0J0VGhRYlNtdjJpM2QxVVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D'
        client = StudioYClient()
        account_result = client.get_account_id_by_short_code(account_code)
        accountId = account_result['data']
        set_result = client.set_cookie(accountId, cookie)
        cookie = client.get_cookie(accountId)['data']
        assert cookie == cookie
