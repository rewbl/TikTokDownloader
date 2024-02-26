from unittest import TestCase

from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config.AppConfig import create_test_core_params, TestUserId
from src.config.RuntimeParameters import RuntimeCoreParameters


class UserEndpoint(EndpointBase):
    user_api = "https://www.douyin.com/aweme/v1/web/user/profile/other/"  # 账号详细数据API

    def __init__(self, params: RuntimeCoreParameters, sec_user_id: str,
                 cookie: str = None, ):
        super().__init__(params, cookie)
        self.sec_user_id = sec_user_id

    @retry
    def run(self) -> dict:
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "publish_video_strategy_type": "2",
            "source": "channel_pc_web",
            "sec_user_id": self.sec_user_id,
            "personal_center_strategy": "1",
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }
        self.deal_url_params(params)
        if not (
                data := self.send_request(
                    self.user_api,
                    params=params,
                )):
            self.log.warning("获取账号数据失败")
            return {}
        try:
            return data["user"] or {}
        except KeyError:
            self.log.error(f"账号数据响应内容异常: {data}")
            return {}

class TestUserEndpoint(TestCase):
    def test_run(self):
        pass
        user_endpoint = UserEndpoint(create_test_core_params(), 'MS4wLjABAAAAFLiU7BSSGKleJ6lkprNLcvgYIDnsUgLiMLOvdgm4xF4')
        user_endpoint.run()
