from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.DouyinEndpoints.WorksEndpoint import WorksEndpoint
from src.Infrastructure.tools import retry
from src.config import Parameter
from src.extract import Extractor


class MixEndpoint(EndpointBase):
    mix_api = "https://www.douyin.com/aweme/v1/web/mix/aweme/"  # 合集API

    def __init__(
            self,
            params: Parameter,
            mix_id: str = None,
            works_id: str = None,
            cookie: str = None, ):
        super().__init__(params, cookie)
        self.works = WorksEndpoint(params, item_id=works_id, tiktok=False)
        self.mix_id = mix_id
        self.works_id = works_id

    def run(self) -> list:
        self._get_mix_id()
        if not self.mix_id:
            return []
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取合集作品数据", total=None)
            while not self.finished:
                progress.update(task_id)
                self._get_mix_data(finished=True)
                # break  # 调试代码
        return self.response

    @retry
    def _get_mix_data(self):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "mix_id": self.mix_id,
            "cursor": self.cursor,
            "count": "20",
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
                    self.mix_api,
                    params=params,
                )):
            self.log.warning("获取合集作品数据失败")
            return False
        try:
            if not (w := data["aweme_list"]):
                raise KeyError
            self.move_list_to_response(w)
            self.cursor = data['cursor']
            self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"合集数据内容异常: {data}")
            self.finished = True
            return False

    def _get_mix_id(self):
        if not self.mix_id:
            self.mix_id = Extractor.extract_mix_id(self.works.run())
