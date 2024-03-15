from typing import Any, List, Dict
from unittest import TestCase, IsolatedAsyncioTestCase

from src.DouyinEndpoints.MyInfoEndpoint import MyInfoEndpoint
from src.DouyinEndpoints.EndpointBase import EndpointBase, Encrypter
from src.Infrastructure.tools import retry, timestamp
from src.Services.DouyinScrapingSessionProvider import DouyinServicesInstance
from src.config.AppConfig import create_test_core_params, TestUserId
from src.config.RuntimeParameters import RuntimeCoreParameters
from src.extract import Extractor


class AwemeCollectionRequest:
    ...
    sec_user_id: str
    cursor: str

    def fill_api_params(self, params):
        params["sec_user_id"] = self.sec_user_id
        params["cursor"] = self.cursor

    def __init__(self, sec_user_id: str = None, cursor: str = None):
        self.sec_user_id = sec_user_id
        self.cursor = cursor


class AwemeCollectionResponse:
    confirmed_success: bool
    cursor: str
    raw_data: Any
    aweme_list: list[dict]
    has_more: int
    status_code: int

    def __init__(self, cursor: str = None, raw_data: Any = None, aweme_list: list[dict] = None,
                 has_more: int = None, status_code: int = None):
        self.cursor = cursor
        self.raw_data = raw_data
        self.aweme_list = aweme_list or []
        self.has_more = has_more
        self.status_code = status_code
        self.confirm_success = False

    @staticmethod
    def from_dict(obj: Any) -> 'AwemeCollectionResponse':
        result = AwemeCollectionResponse()
        result.raw_data = obj
        result.cursor = obj.get("cursor")
        result.aweme_list = obj.get("aweme_list")
        result.has_more = obj.get("has_more")
        result.status_code = obj.get("status_code")
        result.check_success()
        return result

    def check_success(self):
        self.confirmed_success = 'aweme_list' in self.raw_data and 'has_more' in self.raw_data

class AwemeCollectionPrivateApi(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/aweme/listcollection/"  # 收藏API
    api_params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "publish_video_strategy_type": "2",
        "pc_client_type": "1",
        "version_code": "170400",
        "version_name": "17.4.0",
        "cookie_enabled": "true",
        "platform": "PC",
        "downlink": "10",
    }

    def __init__(self, params: RuntimeCoreParameters):
        cookie = 'store-region-src=uid; LOGIN_STATUS=1; __security_server_data_status=1; _bd_ticket_crypt_cookie=771cf1301b938695d7a1792f117caf92; _bd_ticket_crypt_doamin=2; d_ticket=be73d5c303cf7ba59baf6d77b3c6b3afeb119; store-region=cn-hn; my_rd=2; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; xgplayer_user_id=839818690335; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; ttwid=1%7C-7d2J6QheXNJBQHvTiAE6vkyaun4OLo_7Gjzq-TAmoo%7C1708143114%7C559ef741577955a187969771bf153b730d0bc77ce105ba69dfd689b7947283dc; passport_csrf_token=4c812de13cc1211e038f38ef0bdcf456; passport_csrf_token_default=4c812de13cc1211e038f38ef0bdcf456; bd_ticket_guard_client_web_domain=2; dy_swidth=3840; dy_sheight=2160; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; xgplayer_device_id=52703508981; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; download_guide=%222%2F20240307%2F0%22; pwa2=%220%7C0%7C2%7C0%22; passport_assist_user=CktOtIzfbFympTViuaxDAPHgyU7tFxdfLJ_IQ3WT_a1OiynX5kE7E7SzM4QODdXUObnkZD_a-I5Rw0m9bF1vtzRqnTHpAPAiAA88VpIaSgo8Bf29X3wt7H9-MutMriejP3PCKj1NLK8xVJPbrylb73u_m1yVztL5zL6oj9dD9Jzvb6vcRn2jBFY_WLIdEJauyw0Yia_WVCABIgEDK-uPbA%3D%3D; sso_uid_tt=c66172b292a4134ed66b0839f1128120; sso_uid_tt_ss=c66172b292a4134ed66b0839f1128120; toutiao_sso_user=57094aeeb3506c774dd250d7c93ad342; toutiao_sso_user_ss=57094aeeb3506c774dd250d7c93ad342; sid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; ssid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; passport_auth_status=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; passport_auth_status_ss=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; uid_tt=842dc94e71572b3e2c63d25db2115258; uid_tt_ss=842dc94e71572b3e2c63d25db2115258; sid_tt=660e6ee9becc05fd6ac177b6f3c91e20; sessionid=660e6ee9becc05fd6ac177b6f3c91e20; sessionid_ss=660e6ee9becc05fd6ac177b6f3c91e20; sid_guard=660e6ee9becc05fd6ac177b6f3c91e20%7C1709861492%7C5183998%7CTue%2C+07-May-2024+01%3A31%3A30+GMT; sid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; ssid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; strategyABtestKey=%221710289637.73%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; publish_badge_show_info=%220%2C0%2C0%2C1710289638660%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710313200000%2F0%2F1710289639364%2F0%22; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; __ac_nonce=065f23cfc00890c35bb2f; __ac_signature=_02B4Z6wo00f014eN-dQAAIDCGxZKGmhpfn-Hrf1AAIQZlhoVYMPmle3UudNwUhgp5B3xb3Xlh0lbkCkPD7gbZEW74Yigqe9XJd6Gvt4-SOR-kFm7QTiQ1Dw35ZQkWqmP.DZGRCRpS26Vk.Pd73; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.45%2C%5C%22effective_type%5C%22%3A%5C%223g%5C%22%2C%5C%22round_trip_time%5C%22%3A300%7D%22; csrf_session_id=0c09746c356341951759e149548056db; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRUZMM0N1NGxtQWFUT2lPQWRCWHUvZnowVnUwRlNXNkdhRnYrM1dyMHYvN1AzcXZiN2dsakU1VHBjZjJuczcvVUd0NER5a0J0VGhRYlNtdjJpM2QxVVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; msToken=qBqFgqOc_to8A8jVWF0lTMqasb0AoVid0kU5XH7m_R9Gl0DLVJRdRyAO-WZyuqwe0Uns3y90hcRIwHm6rPjrKl3AmsxYu_mhAy1ZUcT-4DoIQ8Ha0eyO; passport_fe_beating_status=true; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710399600000%2F0%2F1710374165650%2F0%22; tt_scid=8FdguyQBwnDuxbRhHgg6Lf0HYzDcSZK.Ac1wbOxNXBAv6zp5SxtOpKiGkhgC.dVt4777; msToken=LjaF5td80PoHV0WnE0hhE-szkS_QTvz9brsS_I5Snb_6zTt7OTKhK5vATVQy3AzsBoiHXsPjrQnbp_kBCXIfKhwhs2sdu1f6faQEu5a-GOcJWR62Qrba; home_can_add_dy_2_desktop=%221%22; IsDouyinActive=true; odin_tt=6f7eb88ee2ca201b63a44a89005a47aee579e4e8f258eb8fa7b7132f1a92458098844f50a2470fc0d8eae3ea71626cbc'

        super().__init__(cookie=cookie)

    @retry
    def request(self, request: AwemeCollectionRequest) -> AwemeCollectionResponse:
        params = self.api_params.copy()
        request.fill_api_params(params)
        msToken='LjaF5td80PoHV0WnE0hhE-szkS_QTvz9brsS_I5Snb_6zTt7OTKhK5vATVQy3AzsBoiHXsPjrQnbp_kBCXIfKhwhs2sdu1f6faQEu5a-GOcJWR62Qrba'
        Encrypter.encrypt_request(params, msToken, 8)

        form = {
            "count": "30",
            "cursor": request.cursor,
        }
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    data=form,
                    method='post')):
            return AwemeCollectionResponse.from_dict({})
        return AwemeCollectionResponse.from_dict(data)

class IAwemeCollectionRecipient:
    def on_aweme_collection(self, aweme_list: List[Dict]) -> bool:
        return bool(aweme_list)

class AwemeCollection:
    __last_request: AwemeCollectionRequest | None
    __last_response: AwemeCollectionResponse | None
    __last_success_response: AwemeCollectionResponse | None
    __can_continue: bool
    __load_complete: bool

    def __init__(self, recipient: IAwemeCollectionRecipient = None):
        self.recipient = recipient
        self.session = DouyinServicesInstance.get_session()
        self.api = AwemeCollectionPrivateApi(create_test_core_params())
        self.__last_request = None
        self.__last_response = None
        self.__can_continue = True
        self.__load_complete = False
        self.__last_retry = 0
        self.__has_error = False

    async def load_full_list(self):
        while self.__can_continue and not self.__load_complete:
            await self.__load_next_page()

    async def __load_next_page(self):
        self.__last_response = self.api.request(self.__next_page_request)

        if self.__last_response.confirmed_success:
            await self.__process_success_response()
        else:
            await self.__process_failed_response()

    @property
    def __next_page_request(self) -> AwemeCollectionRequest:
        cursor = self.__last_response.cursor if self.__last_response else None
        self.__last_request = AwemeCollectionRequest(cursor=cursor)
        return self.__last_request

    async def __process_success_response(self):
        self.__last_retry = 0
        self.__last_success_response = self.__last_response
        self.__load_complete = not self.__last_response.has_more

        if self.recipient:
            self.__can_continue = self.recipient.on_aweme_collection(self.__last_response.aweme_list)

    @property
    def __can_retry(self):
        return self.__last_retry < 3

    async def __process_failed_response(self):
        if not self.__can_retry:
            self.__can_continue = False
            self.__load_complete = True
            self.__has_error = True
            return
        self.__last_retry += 1


class TestAwemeCollectionPrivateApi(IsolatedAsyncioTestCase):

    def test_request(self):
        api = AwemeCollectionPrivateApi(create_test_core_params())
        request = AwemeCollectionRequest(sec_user_id=TestUserId)
        response = api.request(request)

        self.assertIsNotNone(response)
        self.assertEqual(len(response.aweme_list), 30)


