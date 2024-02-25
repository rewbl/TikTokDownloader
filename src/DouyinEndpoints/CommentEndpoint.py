from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry
from src.config import Parameter
from src.extract import Extractor


class CommentEndpoint(EndpointBase):
    comment_api = "https://www.douyin.com/aweme/v1/web/comment/list/"  # 评论API
    comment_api_reply = "https://www.douyin.com/aweme/v1/web/comment/list/reply/"  # 评论回复API

    def __init__(self, params: Parameter, item_id: str, pages: int = None,
                 cookie: str = None, ):
        super().__init__(params, cookie)
        self.item_id = item_id
        self.pages = pages or params.max_pages
        self.all_data = None
        self.reply_ids = None

    def run(self, extractor: Extractor, recorder, source=False) -> list[dict]:
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取作品评论数据", total=None)
            while not self.finished and self.pages > 0:
                progress.update(task_id)
                self.get_comments_data(self.comment_api, finished=True)
                self.pages -= 1
                # break  # 调试代码
        self.all_data, self.reply_ids = extractor.run(
            self.response, recorder, "comment", source=source)
        self.response = []
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取评论回复数据", total=None)
            for i in self.reply_ids:
                self.finished = False
                self.cursor = 0
                while not self.finished and self.pages > 0:
                    progress.update(task_id)
                    self.get_comments_data(
                        self.comment_api_reply, i, finished=True)
                    self.pages -= 1
                    # break  # 调试代码
        self.all_data.extend(
            self._check_reply_ids(
                *
                extractor.run(
                    self.response,
                    recorder,
                    "comment",
                    source=source)))
        return self.all_data

    @retry
    def get_comments_data(self, api: str, reply=""):
        if reply:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "item_id": self.item_id,
                "comment_id": reply,
                "whale_cut_token": "",
                "cut_version": "1",
                "cursor": self.cursor,
                "count": "10" if self.cursor else "3",
                "item_type": "0",
                "pc_client_type": "1",
                "version_code": "170400",
                "version_name": "17.4.0",
                "cookie_enabled": "true",
                "platform": "PC",
                "downlink": "10",
            }
            if not self.cursor:
                del params["whale_cut_token"]
        else:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "aweme_id": self.item_id,
                "cursor": self.cursor,
                "count": "20",
                "item_type": "0",
                "insert_ids": "",
                "whale_cut_token": "",
                "cut_version": "1",
                "rcFT": "",
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
                    api,
                    params=params)):
            self.log.warning("获取作品评论数据失败")
            return False
        try:
            if c := data["comments"]:
                self.move_list_to_response(c)
            self.cursor = data["cursor"]
            self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"作品评论数据响应内容异常: {data}")
            self.finished = True
            return False

    @staticmethod
    def _check_reply_ids(data: list[dict], ids: list) -> list[dict]:
        if ids:
            raise ValueError
        return data
