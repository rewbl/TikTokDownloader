from typing import Any, List, Dict
from unittest import TestCase, IsolatedAsyncioTestCase

from src.DouyinEndpoints.MyInfoEndpoint import MyInfoEndpoint
from src.DouyinEndpoints.EndpointBase import EndpointBase
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
        cookie = '__ac_nonce=065f242f300626128c9c5; __ac_signature=_02B4Z6wo00f01mr9LbgAAIDAi.3OuOhcJE5q3SkAAP9c85; ttwid=1%7Cy_Yif1WKgFl7mRyfgtHg0xZuvXFOFp_ze1GnjB8We4k%7C1710375670%7C660d83cae745477a21e88ef0d5b412cff75d00a5fdc464eac0fe7c62e22947dc; douyin.com; device_web_cpu_core=24; device_web_memory_size=8; architecture=amd64; dy_swidth=3840; dy_sheight=2160; strategyABtestKey=%221710375677.549%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; csrf_session_id=b3f0a1a2049bc50dc08891ea42288bc4; xgplayer_user_id=455156790902; ttcid=ff122030a4b04aaa947e229fee147ba636; GlobalGuideTimes=%221710375689%7C1%22; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; passport_csrf_token=e4e3964f490d60fba25d91844a8525f3; passport_csrf_token_default=e4e3964f490d60fba25d91844a8525f3; bd_ticket_guard_client_web_domain=2; passport_assist_user=Cj8GFMtFgqBf-OBtJQvcovtOE_E4ICVjqS5WnLcTYh-hyR0ZxRK7DIec6QVba9MmxK4aGSJg_8YiBG9XGrWXlCoaSgo8To0amt1XlLYTx2FLFg6A2Aj4dmg3bLIj12PqE9y-7uFQylPxtPTm8fYXkL2kgFnxlIbSgonabT-gW1hdEPfvyw0Yia_WVCABIgEDQ9dKwg%3D%3D; n_mh=ToxDUIP1EE3Cs1qx5eTeCuSc1F_HYF22_NWbPp3NqWA; sso_uid_tt=183747c20dd1b6f51f7d21b83df1fa68; sso_uid_tt_ss=183747c20dd1b6f51f7d21b83df1fa68; toutiao_sso_user=4cde23f294bb80744499ecd2d41cba9c; toutiao_sso_user_ss=4cde23f294bb80744499ecd2d41cba9c; sid_ucp_sso_v1=1.0.0-KDI4OWViMGNjNGU4ZmM0NjBlODY5Y2UxMmQxZTc4ZDkzNjU4YzIwZGMKHgjj0KC48M0MEK-Gya8GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDRjZGUyM2YyOTRiYjgwNzQ0NDk5ZWNkMmQ0MWNiYTlj; ssid_ucp_sso_v1=1.0.0-KDI4OWViMGNjNGU4ZmM0NjBlODY5Y2UxMmQxZTc4ZDkzNjU4YzIwZGMKHgjj0KC48M0MEK-Gya8GGO8xIAwwguLBpwY4BkD0BxoCbGYiIDRjZGUyM2YyOTRiYjgwNzQ0NDk5ZWNkMmQ0MWNiYTlj; passport_auth_status=dd6345e80bf53c09f0dfd5e1fe8955f9%2C; passport_auth_status_ss=dd6345e80bf53c09f0dfd5e1fe8955f9%2C; uid_tt=ad1eebeae99839d811bbd16bdea37b87; uid_tt_ss=ad1eebeae99839d811bbd16bdea37b87; sid_tt=080d3a22a620fa47c895224a95c02174; sessionid=080d3a22a620fa47c895224a95c02174; sessionid_ss=080d3a22a620fa47c895224a95c02174; LOGIN_STATUS=1; _bd_ticket_crypt_doamin=2; _bd_ticket_crypt_cookie=1dcec6c252fa84065b05ede8b2e2bee9; __security_server_data_status=1; store-region=de; store-region-src=uid; publish_badge_show_info=%220%2C0%2C0%2C1710375733070%22; sid_guard=080d3a22a620fa47c895224a95c02174%7C1710375734%7C5183996%7CMon%2C+13-May-2024+00%3A22%3A10+GMT; sid_ucp_v1=1.0.0-KGJmNmI0YzcyMzc5Njk1YzgwMDQxYjY2MTc0NmU1ZjhmMTBlZTljZjkKGgjj0KC48M0MELaGya8GGO8xIAw4BkD0B0gEGgJscSIgMDgwZDNhMjJhNjIwZmE0N2M4OTUyMjRhOTVjMDIxNzQ; ssid_ucp_v1=1.0.0-KGJmNmI0YzcyMzc5Njk1YzgwMDQxYjY2MTc0NmU1ZjhmMTBlZTljZjkKGgjj0KC48M0MELaGya8GGO8xIAw4BkD0B0gEGgJscSIgMDgwZDNhMjJhNjIwZmE0N2M4OTUyMjRhOTVjMDIxNzQ; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAJKIOm63UxSmQMRAyiM43eGYA3R3qR6-rtr4jtAA_iQo%2F1710399600000%2F0%2F1710375733657%2F0%22; s_v_web_id=verify_ltqhk02x_hNmWiPQ5_j8kq_4VLH_ABC8_mGojKNsFxQwc; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A1%7D%22; download_guide=%220%2F%2F1%22; xg_device_score=7.243616653118665; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAJKIOm63UxSmQMRAyiM43eGYA3R3qR6-rtr4jtAA_iQo%2F1710399600000%2F0%2F1710375909745%2F0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCTjVZSXZqS3BuL2xNV1BzTTc5bmtUV291U0lEeDJzUklYa3U0WWNXdVI5OVE5SnhibEpBNnBUOU56TVROaVRKa1ZJTWlDVUNXZDJ1a216cmloaEFLQWc9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; tt_scid=OmM6.Efvt6wqFak7KXUeaScd0ftr5nit4fozhuNpUwEq8CHAyPE5hE.BFLPvQUJ.bf01; pwa2=%220%7C0%7C2%7C0%22; odin_tt=2d2f95206d16a3c65fc2e62feb953f6fbdd15248780671423b2c6deade56de66be2ea3629db646d991409b7d44bef1a7663dffd5ec3303e74a507d38f3d6ddab; msToken=OzOcctJY3yB2LEUzqX9_-woya344hrKXX2tlOuK4SDhB28dOY3u3NvdZKbztTsfRglRmfZIFtfgv0H4Ct9bqY_obCWzTxaFUiDl_t-KTo-BLky1yeIAMX08h97b8zNo=; msToken=NaV4Nj5uxdJqPnqO6xXRjhln0UBgrHOWQbCuUz49eIZ_-4RHnAyHQG9jGEgj4c9v9W2FdfxXc8wDs6_vQMOoyd_3GSjx9Nz02J8L_3dIvAKMlmw24ZZ2SaSoY2VWej8=; passport_fe_beating_status=false; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A24%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.25%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22'
        cookie = 'store-region-src=uid; LOGIN_STATUS=1; __security_server_data_status=1; _bd_ticket_crypt_cookie=771cf1301b938695d7a1792f117caf92; _bd_ticket_crypt_doamin=2; d_ticket=be73d5c303cf7ba59baf6d77b3c6b3afeb119; store-region=cn-hn; my_rd=2; n_mh=9-mIeuD4wZnlYrrOvfzG3MuT6aQmCUtmr8FxV8Kl8xY; xgplayer_user_id=839818690335; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; ttwid=1%7C-7d2J6QheXNJBQHvTiAE6vkyaun4OLo_7Gjzq-TAmoo%7C1708143114%7C559ef741577955a187969771bf153b730d0bc77ce105ba69dfd689b7947283dc; passport_csrf_token=4c812de13cc1211e038f38ef0bdcf456; passport_csrf_token_default=4c812de13cc1211e038f38ef0bdcf456; bd_ticket_guard_client_web_domain=2; dy_swidth=3840; dy_sheight=2160; s_v_web_id=verify_lspkkpg0_DKvqjhdr_bQXa_4mYu_9nMp_Oyr77OwoptMT; xgplayer_device_id=52703508981; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; download_guide=%222%2F20240307%2F0%22; pwa2=%220%7C0%7C2%7C0%22; passport_assist_user=CktOtIzfbFympTViuaxDAPHgyU7tFxdfLJ_IQ3WT_a1OiynX5kE7E7SzM4QODdXUObnkZD_a-I5Rw0m9bF1vtzRqnTHpAPAiAA88VpIaSgo8Bf29X3wt7H9-MutMriejP3PCKj1NLK8xVJPbrylb73u_m1yVztL5zL6oj9dD9Jzvb6vcRn2jBFY_WLIdEJauyw0Yia_WVCABIgEDK-uPbA%3D%3D; sso_uid_tt=c66172b292a4134ed66b0839f1128120; sso_uid_tt_ss=c66172b292a4134ed66b0839f1128120; toutiao_sso_user=57094aeeb3506c774dd250d7c93ad342; toutiao_sso_user_ss=57094aeeb3506c774dd250d7c93ad342; sid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; ssid_ucp_sso_v1=1.0.0-KDc0MDk4NjQ0MTYxNTJkZTBlNjFjZmNlNjcwYzRhZGNhYjVmODNlYTgKHwjq77CrwM2KBhDu1KmvBhjvMSAMMPysga4GOAZA9AcaAmhsIiA1NzA5NGFlZWIzNTA2Yzc3NGRkMjUwZDdjOTNhZDM0Mg; passport_auth_status=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; passport_auth_status_ss=6c67e8873f1d276ecf22cb4ce321e979%2C031079c2957d596d4f8dac2527b38dbc; uid_tt=842dc94e71572b3e2c63d25db2115258; uid_tt_ss=842dc94e71572b3e2c63d25db2115258; sid_tt=660e6ee9becc05fd6ac177b6f3c91e20; sessionid=660e6ee9becc05fd6ac177b6f3c91e20; sessionid_ss=660e6ee9becc05fd6ac177b6f3c91e20; sid_guard=660e6ee9becc05fd6ac177b6f3c91e20%7C1709861492%7C5183998%7CTue%2C+07-May-2024+01%3A31%3A30+GMT; sid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; ssid_ucp_v1=1.0.0-KDE4ZjQ0MmUzNzZiYTQwMjZlZDQ1NDNlZjA2ZjViYjU2YTI1YjAwYjQKGwjq77CrwM2KBhD01KmvBhjvMSAMOAZA9AdIBBoCbGYiIDY2MGU2ZWU5YmVjYzA1ZmQ2YWMxNzdiNmYzYzkxZTIw; strategyABtestKey=%221710289637.73%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.5%7D; publish_badge_show_info=%220%2C0%2C0%2C1710289638660%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710313200000%2F0%2F1710289639364%2F0%22; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; __ac_nonce=065f23cfc00890c35bb2f; __ac_signature=_02B4Z6wo00f014eN-dQAAIDCGxZKGmhpfn-Hrf1AAIQZlhoVYMPmle3UudNwUhgp5B3xb3Xlh0lbkCkPD7gbZEW74Yigqe9XJd6Gvt4-SOR-kFm7QTiQ1Dw35ZQkWqmP.DZGRCRpS26Vk.Pd73; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A3840%2C%5C%22screen_height%5C%22%3A2160%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A1.45%2C%5C%22effective_type%5C%22%3A%5C%223g%5C%22%2C%5C%22round_trip_time%5C%22%3A300%7D%22; csrf_session_id=0c09746c356341951759e149548056db; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCRUZMM0N1NGxtQWFUT2lPQWRCWHUvZnowVnUwRlNXNkdhRnYrM1dyMHYvN1AzcXZiN2dsakU1VHBjZjJuczcvVUd0NER5a0J0VGhRYlNtdjJpM2QxVVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; msToken=qBqFgqOc_to8A8jVWF0lTMqasb0AoVid0kU5XH7m_R9Gl0DLVJRdRyAO-WZyuqwe0Uns3y90hcRIwHm6rPjrKl3AmsxYu_mhAy1ZUcT-4DoIQ8Ha0eyO; passport_fe_beating_status=true; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAfCqumJYlOkuY9IaFspLpqPzJe29lv2XV5J8buj7PboZm5cgDduJaxzpJp0yLCRcG%2F1710399600000%2F0%2F1710374165650%2F0%22; tt_scid=8FdguyQBwnDuxbRhHgg6Lf0HYzDcSZK.Ac1wbOxNXBAv6zp5SxtOpKiGkhgC.dVt4777; msToken=LjaF5td80PoHV0WnE0hhE-szkS_QTvz9brsS_I5Snb_6zTt7OTKhK5vATVQy3AzsBoiHXsPjrQnbp_kBCXIfKhwhs2sdu1f6faQEu5a-GOcJWR62Qrba; home_can_add_dy_2_desktop=%221%22; IsDouyinActive=true; odin_tt=6f7eb88ee2ca201b63a44a89005a47aee579e4e8f258eb8fa7b7132f1a92458098844f50a2470fc0d8eae3ea71626cbc'
        super().__init__(params, cookie=cookie)

    @retry
    def request(self, request: AwemeCollectionRequest) -> AwemeCollectionResponse:
        params = self.api_params.copy()
        request.fill_api_params(params)
        self.deal_url_params(params)
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
            self.log.warning("获取账号收藏数据失败")
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

    async def test_list(self):
        collection = AwemeCollection(IAwemeCollectionRecipient())
        await collection.load_full_list()
        breakpoint()



class CollectionEndpoint(EndpointBase):
    collection_api = "https://www.douyin.com/aweme/v1/web/aweme/listcollection/"  # 收藏API
    params = {
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

    def __init__(self, params: RuntimeCoreParameters, sec_user_id: str,
                 pages: int = None, ):
        super().__init__(params)
        self.pages = pages
        self.sec_user_id = bool(sec_user_id)
        self.info = MyInfoEndpoint(params, sec_user_id)

    def run(self):
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取账号收藏数据", total=None)
            while not self.finished and self.pages > 0:
                progress.update(task_id)
                self._get_account_data(finished=True)
                self.pages -= 1
        self._get_owner_data()
        return self.response

    @retry
    def _get_account_data(self):
        params = self.params.copy()
        self.deal_url_params(params)
        form = {
            "count": "30",
            "cursor": self.cursor,
        }
        if not (
                data := self.send_request(
                    self.collection_api,
                    params=params,
                    data=form,
                    method='post')):
            self.log.warning("获取账号收藏数据失败")
            return False
        try:
            self.cursor = data['cursor']
            self.move_list_to_response(data["aweme_list"])
            self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"账号收藏数据响应内容异常: {data}")
            self.finished = True
            return False

    def _get_owner_data(self):
        if not any(self.response):
            return
        if self.sec_user_id and (
                info := Extractor.get_user_info(
                    self.info.run())):
            self.response.append({"author": info})
        else:
            temp_data = timestamp()
            self.log.warning(
                f"owner_url 参数未设置 或者 获取账号数据失败，本次运行将临时使用 {temp_data} 作为账号昵称和 UID")
            temp_dict = {
                "author": {
                    "nickname": temp_data,
                    "uid": temp_data,
                }
            }
            self.response.append(temp_dict)


class TestCollectionEndpoint(TestCase):

    def test_run(self):
        CollectionEndpoint(create_test_core_params(), TestUserId).run()
