import urllib3
from urllib3.exceptions import InsecureRequestWarning

from src.Infrastructure.encrypt import XBogus
from src.Infrastructure.module import ColorfulConsole
from src.Infrastructure.module.cookie import generate_cookie
from src.Infrastructure.record import BaseLogger, LoggerManager
from src.config.RuntimeParameters import RuntimeCoreParameters

urllib3.disable_warnings(InsecureRequestWarning)

XBogusInstance = XBogus()
TestUserId='MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG'

TestCookie = {
    "n_mh": "9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY",
    "LOGIN_STATUS": "1",
    "_bd_ticket_crypt_doamin": "2",
    "__security_server_data_status": "1",
    "store-region": "cn-hn",
    "store-region-src": "uid",
    "my_rd": "2",
    "xgplayer_user_id": "839818690335",
    "dy_swidth": "3840",
    "dy_sheight": "2160",
    "bd_ticket_guard_client_web_domain": "2",
    "d_ticket": "be73d5c303cf7ba59baf6d77b3c6b3afeb119",
    "sso_uid_tt": "798a6aedef5393f0a81b932b1e86ee84",
    "sso_uid_tt_ss": "798a6aedef5393f0a81b932b1e86ee84",
    "toutiao_sso_user": "a5d6848d6d7c6028c7612712ded21741",
    "toutiao_sso_user_ss": "a5d6848d6d7c6028c7612712ded21741",
    "_bd_ticket_crypt_cookie": "771cf1301b938695d7a1792f117caf92",
    "passport_assist_user": "CksgNQqyXuckOK9isKMrPt3I0dZ5RN-RhCRbeAQ8O_4jvc-lQaktlHbbRy3P9SkbVCgxxdOiDIsMcOfI2xiIXWDXgXm9guHB5-vwS2UaSgo8mDZlLPHDCEgF_KeQ3JTBNGWMeOJ8LYmQmNQwzSvVaOwVb6I1wGuoVtlTdHK8_w6I5BvIEwWXjiFSg4eoEKfNyQ0Yia_WVCABIgEDaXhSFA%3D%3D",
    "publish_badge_show_info": "%221%2C0%2C0%2C1708143705653%22",
    "s_v_web_id": "verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT",
    "passport_csrf_token": "4c812de13cc1211e038f38ef0bdcf456",
    "passport_csrf_token_default": "4c812de13cc1211e038f38ef0bdcf456",
    "download_guide": "%222%2F20240217%2F0%22",
    "volume_info": "%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D",
    "sid_ucp_sso_v1": "1.0.0-KGFlYjNkYjg3MzE4YTBjODJiNzY4MDgyZGRhYzA2NWY3NzgxZGRhNWEKHwjq77CrwM2KBhCG6cCuBhjvMSAMMPysga4GOAZA9AcaAmxmIiBhNWQ2ODQ4ZDZkN2M2MDI4Yzc2MTI3MTJkZWQyMTc0MQ",
    "ssid_ucp_sso_v1": "1.0.0-KGFlYjNkYjg3MzE4YTBjODJiNzY4MDgyZGRhYzA2NWY3NzgxZGRhNWEKHwjq77CrwM2KBhCG6cCuBhjvMSAMMPysga4GOAZA9AcaAmxmIiBhNWQ2ODQ4ZDZkN2M2MDI4Yzc2MTI3MTJkZWQyMTc0MQ",
    "sid_guard": "121acf774665d1d9b372312dcf3002c7%7C1708143757%7C5183996%7CWed%2C+17-Apr-2024+04%3A22%3A33+GMT",
    "uid_tt": "07b99c1682480c2a98327d34bb1948b0",
    "uid_tt_ss": "07b99c1682480c2a98327d34bb1948b0",
    "sid_tt": "121acf774665d1d9b372312dcf3002c7",
    "sessionid": "121acf774665d1d9b372312dcf3002c7",
    "sessionid_ss": "121acf774665d1d9b372312dcf3002c7",
    "sid_ucp_v1": "1.0.0-KGQxMmExYTVhMmZmZjUzYWJlODFkMmJiYWRmOTQ3ZGI5YzE4OTlhYzgKGwjq77CrwM2KBhCN6cCuBhjvMSAMOAZA9AdIBBoCbGYiIDEyMWFjZjc3NDY2NWQxZDliMzcyMzEyZGNmMzAwMmM3",
    "ssid_ucp_v1": "1.0.0-KGQxMmExYTVhMmZmZjUzYWJlODFkMmJiYWRmOTQ3ZGI5YzE4OTlhYzgKGwjq77CrwM2KBhCN6cCuBhjvMSAMOAZA9AdIBBoCbGYiIDEyMWFjZjc3NDY2NWQxZDliMzcyMzEyZGNmMzAwMmM3",
    "pwa2": "%220%7C0%7C3%7C0%22",
    "strategyABtestKey": "%221708142931.936%22",
    "__ac_nonce": "065d041a70006ca1ac6e1",
    "__ac_signature": "_02B4Z6wo00f01gzM2RgAAIDAguTzsgGyO9IM7N2AAObxbNCFaI01aEI0e4ewjIelsaUStROTIbukC8wie44.R-A7WRz0cdNecQ6y7TJm94801uVZoRTIziOEjoyQP2CjGV2CWO9tOCGYpz8a78",
    "FOLLOW_LIVE_POINT_INFO": "%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1708185600000%2F0%2F0%2F1708148931427%22",
    "stream_recommend_feed_params": "%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22",
    "bd_ticket_guard_client_data": "eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRmVFTWFkRkljVVcvSFVqT3J3dHozMkdtZlJJM0Ftem1PbExQd2Q5OHlPajV2LzU1VVpjNkFpd3NkYWhzZSs0bTd5eWppV1UxTXRKQU50WGlXeHVqZnc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D",
    "home_can_add_dy_2_desktop": "%221%22",
    "tt_scid": "Xp7f.7y4JG4GPWrht-y1ymOrtN9jlXEhU.McSlfYv92qjJRPuJjW4t8MdRyiy5hI6f77",
    "stream_player_status_params": "%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22",
    "odin_tt": "90b1f4062e93b89b7ddcd4ea90ac75ea9ea8e6e0161f00bca272fd27f408146ef9a65306212c188604fc10802b99771969946c01621a779f15cc73a2c77e2516",
    "FOLLOW_NUMBER_YELLOW_POINT_INFO": "%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1708185600000%2F0%2F0%2F1708149531374%22",
    "IsDouyinActive": "false"
  }


def create_test_core_params():
    params = RuntimeCoreParameters()
    params.cookie = TestCookie
    params.console = ColorfulConsole()
    params.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": generate_cookie(params.cookie)
    }
    params.logger = LoggerManager('', params.console)
    params.proxies = {'http':None, 'https':None, 'ftp':None}
    # params.update_cookie_session()
    return params
