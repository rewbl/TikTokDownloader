from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import RuntimeParameters
from src.config.RuntimeParameters import RuntimeCoreParameters


class UserInfoEndpoint(EndpointBase):
    info_api = "https://www.douyin.com/aweme/v1/web/im/user/info/"  # 账号简略数据API

    def __init__(
            self,
            params: RuntimeCoreParameters,
            sec_user_id: str,
            cookie: str = None):
        super().__init__(params, cookie)
        self.sec_user_id = sec_user_id
        self.params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }

    @retry
    def run(self) -> dict:
        self.deal_url_params(self.params)
        form = {
            "sec_user_ids": f'["{self.sec_user_id}"]'
        }
        if not (
                data := self.send_request(
                    self.info_api,
                    params=self.params,
                    method='post',
                    data=form,
                )):
            self.log.warning("获取账号数据失败")
            return {}
        try:
            return data["data"][0] or {}
        except (KeyError, IndexError, TypeError):
            self.log.error(f"账号数据响应内容异常: {data}")
            return {}
