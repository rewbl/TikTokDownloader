from datetime import datetime
from types import SimpleNamespace

from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import Parameter


class HotEndpoint(EndpointBase):
    hot_api = "https://www.douyin.com/aweme/v1/web/hot/search/list/"  # 热榜API
    board_params = (
        SimpleNamespace(
            name="抖音热榜",
            type=0,
            sub_type="",
        ),
        SimpleNamespace(
            name="娱乐榜",
            type=2,
            sub_type=2,
        ),
        SimpleNamespace(
            name="社会榜",
            type=2,
            sub_type=4,
        ),
        SimpleNamespace(
            name="挑战榜",
            type=2,
            sub_type="hotspot_challenge",
        ),
    )

    def __init__(self, params: Parameter):
        super().__init__(params)
        del self.PC_headers["Cookie"]
        self.time = None

    def run(self):
        self.time = f"{datetime.now():%Y_%m_%d_%H_%M_%S}"
        for i, j in enumerate(self.board_params):
            self._get_board_data(i, j)
        return self.time, self.response

    @retry
    def _get_board_data(self, index: int, data: SimpleNamespace):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "detail_list": "1",
            "source": "6",
            "board_type": data.type,
            "board_sub_type": data.sub_type,
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }
        self.deal_url_params(params)
        if not (
                board := self.send_request(
                    self.hot_api,
                    params=params,
                )):
            self.log.warning(f"获取 {data.name} 数据失败")
            return False
        try:
            self.response.append((index, board["data"]["word_list"]))
            return True
        except KeyError:
            self.log.error(f"{data.name} 数据响应内容异常: {board}")
            return False
