from types import SimpleNamespace
from urllib.parse import quote

from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import RuntimeParameters


class SearchEndpoint(EndpointBase):
    search_params = (
        SimpleNamespace(
            api="https://www.douyin.com/aweme/v1/web/general/search/single/",
            count=15,
            channel="aweme_general",
            type="general",
        ),
        SimpleNamespace(
            api="https://www.douyin.com/aweme/v1/web/search/item/",
            count=20,
            channel="aweme_video_web",
            type="video",
        ),
        SimpleNamespace(
            api="https://www.douyin.com/aweme/v1/web/discover/search/",
            count=12,
            channel="aweme_user_web",
            type="user",
        ),
        SimpleNamespace(
            api="https://www.douyin.com/aweme/v1/web/live/search/",
            count=15,
            channel="aweme_live",
            type="live",
        ),
    )

    def __init__(
            self,
            params: RuntimeParameters,
            keyword: str,
            tab=0,
            page=1,
            sort_type=0,
            publish_time=0,
            cookie: str = None, ):
        super().__init__(params, cookie)
        self.keyword = keyword
        self.tab = tab
        self.page = page
        self.sort_type = sort_type
        self.publish_time = publish_time

    def run(self):
        data = self.search_params[self.tab]
        self.PC_headers["Referer"] = (
            f"https://www.douyin.com/search/{            quote(                self.keyword)}?" f"source=switch_tab&type={            data.type}")
        if self.tab in {2, 3}:
            deal = self._run_user_live
        elif self.tab in {0, 1}:
            deal = self._run_general
        else:
            raise ValueError
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取搜索结果数据", total=None)
            while not self.finished and self.page > 0:
                progress.update(task_id)
                deal(data, self.tab)
                self.page -= 1
        return self.response

    def _run_user_live(self, data: SimpleNamespace, type_: int):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "search_channel": data.channel,
            "keyword": self.keyword,
            "search_source": "switch_tab",
            "query_correct_type": "1",
            "is_filter_search": "0",
            "from_group_id": "",
            "offset": self.cursor,
            "count": 10 if self.cursor else data.count,
            "pc_client_type": "1",
            "version_code": "170400",
            "version_name": "17.4.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }
        self.deal_url_params(params, 4 if self.cursor else 8)
        self._get_search_data(
            data.api,
            params,
            "user_list" if type_ == 2 else "data", finished=True)

    def _run_general(self, data: SimpleNamespace, type_: int, *args):
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "search_channel": data.channel,
            "sort_type": self.sort_type,
            "publish_time": self.publish_time,
            "keyword": self.keyword,
            "search_source": "tab_search",
            "query_correct_type": "1",
            "is_filter_search": {True: 1, False: 0}[any((self.sort_type, self.publish_time))],
            "from_group_id": "",
            "offset": self.cursor,
            "count": 10 if self.cursor else data.count,
            "pc_client_type": "1",
            "version_code": "170400" if type_ else "190600",
            "version_name": "17.4.0" if type_ else "19.6.0",
            "cookie_enabled": "true",
            "platform": "PC",
            "downlink": "10",
        }
        self.deal_url_params(params, 4 if self.cursor else 8)
        self._get_search_data(data.api, params, "data", finished=True)

    @retry
    def _get_search_data(self, api: str, params: dict, key: str):
        if not (
                data := self.send_request(
                    api,
                    params=params,
                )):
            self.log.warning("获取搜索数据失败")
            return False
        try:
            self.move_list_to_response(data[key])
            self.cursor = data["cursor"]
            self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"搜索数据响应内容异常: {data}")
            self.finished = True
            return False
