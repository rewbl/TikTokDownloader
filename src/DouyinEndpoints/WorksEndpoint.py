from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import Parameter


class WorksEndpoint(EndpointBase):
    item_api = "https://www.douyin.com/aweme/v1/web/aweme/detail/"
    item_api_tiktok = "https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/"

    def __init__(self, params: Parameter, item_id: str, tiktok: bool,
                 cookie: str = None, ):
        super().__init__(params, cookie)
        self.id = item_id
        self.tiktok = tiktok

    @retry
    def run(self) -> dict:
        if self.tiktok:
            params = {
                "aweme_id": self.id,
            }
            api = self.item_api_tiktok
            headers = self.Phone_headers
        else:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "aweme_id": self.id,
                "pc_client_type": "1",
                "version_code": "190500",
                "version_name": "19.5.0",
                "cookie_enabled": "true",
                "platform": "PC",
                "downlink": "10",
            }
            api = self.item_api
            self.deal_url_params(params)
            headers = None
        if not (
                data := self.send_request(
                    api,
                    params=params,
                    headers=headers,
                )):
            self.log.warning("获取作品数据失败")
            return {}
        try:
            return data["aweme_list"][0] if self.tiktok else data["aweme_detail"] or {}
        except (KeyError, IndexError):
            self.log.error(f"作品数据响应内容异常: {data}")
            return {}
