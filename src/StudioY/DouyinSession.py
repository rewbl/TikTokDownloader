from http.cookiejar import Cookie
from unittest.mock import Mock
from urllib.parse import unquote, quote

import requests
from requests.cookies import RequestsCookieJar

from src.StudioY.StudioYClient import get_account_id_and_cookie, StudioYClient
from src.config.RuntimeParameters import update_cookie_session


class DouyinSession:
    short_code: str
    account_id: str
    cookie: str
    cookie_jar: RequestsCookieJar

    logger = Mock()
    console = Mock()
    proxies = {'http': None, 'https': None, 'ftp': None}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                      "/116.0.0.0 Safari/537.36"
    }

    def __init__(self, short_code: str):
        self.short_code = short_code
        self.account_id = ''
        self.cookie = ''
        self.cookie_jar = RequestsCookieJar()

    def load_session(self):
        self.account_id, self.cookie = get_account_id_and_cookie(self.short_code)
        cookie_dict = self.__cookie_dict(self.cookie)
        update_cookie_session(cookie_dict)
        self.cookie = self.__cookie_dict_to_str(cookie_dict)
        self.__parse_cookie_to_jar()

    @property
    def cookie_header_value(self):
        cookie_list = []
        for cookie in self.cookie_jar:
            cookie_list.append(f"{quote(cookie.name)}={quote(cookie.value)}")
            return '; '.join(cookie_list)

    def upload_cookie(self):
        StudioYClient().set_cookie(self.account_id, self.cookie_header_value)

    def update_cookie_header(self):
        self.headers['Cookie'] = self.cookie_header_value
        self.headers[
            'Cookie'] = 'store-region=cn-hn; __security_server_data_status=1; _bd_ticket_crypt_cookie=771cf1301b938695d7a1792f117caf92; _bd_ticket_crypt_doamin=2; d_ticket=be73d5c303cf7ba59baf6d77b3c6b3afeb119; my_rd=2; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; xgplayer_user_id=839818690335; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; LOGIN_STATUS=1; store-region-src=uid; ttwid=1%7C-7d2J6QheXNJBQHvTiAE6vkyaun4OLo_7Gjzq-TAmoo%7C1708143114%7C559ef741577955a187969771bf153b730d0bc77ce105ba69dfd689b7947283dc; passport_csrf_token=4c812de13cc1211e038f38ef0bdcf456; passport_csrf_token_default=4c812de13cc1211e038f38ef0bdcf456; bd_ticket_guard_client_web_domain=2; dy_swidth=3840; dy_sheight=2160; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; xgplayer_device_id=52703508981; passport_assist_user=CktOtIzfbFympTViuaxDAPHgyU7tFxdfLJ_IQ3WT_a1OiynX5kE7E7SzM4QODdXUObnkZD_a-I5Rw0m9bF1vtzRqnTHpAPAiAA88VpIaSgo8Bf29X3wt7H9-MutMriejP3PCKj1NLK8xVJPbrylb73u_m1yVztL5zL6oj9dD9Jzvb6vcRn2jBFY_WLIdEJauyw0Yia_WVCABIgEDK-uPbA%3D%3D; sso_uid_tt=c66172b292a4134ed66b0839f1128120; sso_uid_tt_ss=c66172b292a4134ed66b0839f1128120; toutiao_sso_user=57094aeeb3506c774dd250d7c93ad342; toutiao_sso_user_ss=57094aeeb3506c774dd250d7c93ad342; sid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; ssid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; passport_auth_status=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; passport_auth_status_ss=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; uid_tt=842dc94e71572b3e2c63d25db2115258; uid_tt_ss=842dc94e71572b3e2c63d25db2115258; sid_tt=660e6ee9becc05fd6ac177b6f3c91e20; sessionid=660e6ee9becc05fd6ac177b6f3c91e20; sessionid_ss=660e6ee9becc05fd6ac177b6f3c91e20; sid_guard=660e6ee9becc05fd6ac177b6f3c91e20%7C1709861492%7C5183998%7CTue%2C+07-May-2024+01%3A31%3A30+GMT; sid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; ssid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; publish_badge_show_info=%220%2C0%2C0%2C1710289638660%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; strategyABtestKey=%221710486710.035%22; tt_scid=jMTBZIelGybOJqnTlQaKEUFXv0F3TyYXOdqyaMd0Q6XZjjdBhLsUfvTcU2aXYNrP844f; __ac_nonce=065f4936f003fb77395f1; __ac_signature=_02B4Z6wo00f01YgAbygAAIDAFJvc5K2cLYmIIGuAAAf11b0pAkpRAxBtASKWp7yYW90KKl3Ki638KQ9YSXl7E1UPqJBUxVok5EMMdohRF772MF6AGsLrofRzJNCt98vPR2MuEbWdDENDGK7U74; douyin.com; xg_device_score=7.535545279985499; device_web_cpu_core=8; device_web_memory_size=8; architecture=amd64; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; csrf_session_id=eaf6df03306bcef8249ac6ea537b2d82; msToken=a0nEBR_GPQKOiFHAaeLOozEMr0VBSGvzm1D9fOuMkTTprJHRzwsaOQGCAz_xeBaHQtGV4jrU3DSnND1yaD_PJzVwG78eeXbSEN0bV8HeM1O-cfD9Px6KRdn1SskkBDw=; passport_fe_beating_status=true; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRUZMM0N1NGxtQWFUT2lPQWRCWHUvZnowVnUwRlNXNkdhRnYrM1dyMHYvN1AzcXZiN2dsakU1VHBjZjJuczcvVUd0NER5a0J0VGhRYlNtdjJpM2QxVVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710572400000%2F0%2F0%2F1710527959124%22; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710572400000%2F0%2F1710527359125%2F0%22; odin_tt=4c868525f0762f4acc41570504c65a09a99abb5cf6fa40019b87d7830cb7630b4678b21be8ed08109fba78daf648d6d8; msToken=z6RmLm-v3clpTs7vWhMuOXrPJYYLSY7oW6pp1eFxmO8zXT8E_4G08afv6UHp87MtHOBZsqWnR7kv_4Sn-kkML7Nr1ZK2fj01Ffim5EjCzwPVmjxh05RMPw=='

    def __parse_cookie_to_jar(self):
        for key, value in self.__cookie_dict(self.cookie).items():
            key = unquote(key)
            value = unquote(value)
            cookie = Cookie(
                version=0,
                name=key,
                value=value,
                port=None,
                port_specified=False,
                domain='"www.douyin.com"',
                domain_specified=False,
                domain_initial_dot=False,
                path='/',
                path_specified=True,
                secure=False,
                expires=None,
                discard=True,
                comment=None,
                comment_url=None,
                rest={'HttpOnly': None},
                rfc2109=False,
            )
            self.cookie_jar.set_cookie(cookie)

    def __cookie_dict(self, cookie: str) -> dict:
        cookie_dict = {}
        for item in cookie.split(';'):
            try:
                key, value = item.strip().split('=', 1)
            except Exception as e:
                continue
            cookie_dict[key] = value
        return cookie_dict

    def __cookie_dict_to_str(self, cookie: dict) -> str:
        cookie_str = ''
        for key, value in cookie.items():
            cookie_str += f'{key}={value};'
        return cookie_str
