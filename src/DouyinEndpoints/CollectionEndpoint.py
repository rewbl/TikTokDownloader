from src.DouyinEndpoints.InfoEndpoint import InfoEndpoint
from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry, timestamp
from src.config import Parameter
from src.extract import Extractor


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

    def __init__(self, params: Parameter, sec_user_id: str,
                 pages: int = None, ):
        super().__init__(params)
        self.pages = pages or params.max_pages
        self.sec_user_id = bool(sec_user_id)
        self.info = InfoEndpoint(params, sec_user_id)

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
            self.deal_item_data(data["aweme_list"])
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
            self.log.warning(f"owner_url 参数未设置 或者 获取账号数据失败，本次运行将临时使用 {            temp_data} 作为账号昵称和 UID")
            temp_dict = {
                "author": {
                    "nickname": temp_data,
                    "uid": temp_data,
                }
            }
            self.response.append(temp_dict)
