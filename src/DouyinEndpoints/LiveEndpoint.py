from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import RuntimeParameters


class LiveEndpoint(EndpointBase):
    live_api = "https://live.douyin.com/webcast/room/web/enter/"
    live_api_share = "https://webcast.amemv.com/webcast/room/reflow/info/"

    def __init__(
            self,
            params: RuntimeParameters,
            web_rid=None,
            room_id=None,
            sec_user_id=None,
            cookie: str = None, ):
        super().__init__(params, cookie)
        self.PC_headers["Referer"] = "https://live.douyin.com/"
        self.web_rid = web_rid
        self.room_id = room_id
        self.sec_user_id = sec_user_id

    def run(self) -> dict:
        if self.web_rid:
            return self.with_web_rid()
        elif self.room_id:
            return self.with_room_id()
        else:
            return {}

    def with_web_rid(self) -> dict:
        params = {
            "aid": "6383",
            "app_name": "douyin_web",
            "device_platform": "web",
            "language": "zh-CN",
            "enter_from": "web_live",
            "cookie_enabled": "true",
            "web_rid": self.web_rid,
        }
        api = self.live_api
        self.deal_url_params(params)
        return self.get_live_data(api, params)

    def with_room_id(self) -> dict:
        params = {
            "type_id": "0",
            "live_id": "1",
            "room_id": self.room_id,
            "sec_user_id": self.sec_user_id,
            "version_code": "99.99.99",
            "app_id": "1128",
        }
        api = self.live_api_share
        headers = self.black_headers
        self.deal_url_params(params, 4)
        return self.get_live_data(api, params, headers)

    @retry
    def get_live_data(
            self,
            api: str,
            params: dict,
            headers: dict = None) -> dict:
        if not (
                data := self.send_request(
                    api,
                    params=params,
                    headers=headers,
                )):
            self.log.warning("获取直播数据失败")
            return {}
        return data or {}
