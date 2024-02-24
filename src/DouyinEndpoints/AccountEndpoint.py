from datetime import date, datetime

from src.DouyinEndpoints.InfoEndpoint import InfoEndpoint
from src.DouyinEndpoints.EndpointBase import EndpointBase
from src.Infrastructure.tools import retry, timestamp
from src.config import Parameter
from src.extract import Extractor


class AccountEndpoint(EndpointBase):
    post_api = "https://www.douyin.com/aweme/v1/web/aweme/post/"
    favorite_api = "https://www.douyin.com/aweme/v1/web/aweme/favorite/"

    def __init__(
            self,
            params: Parameter,
            sec_user_id: str,
            tab="post",
            earliest="",
            latest="",
            pages: int = None,
            cookie: str = None, ):
        super().__init__(params, cookie)
        self.sec_user_id = sec_user_id
        self.api, self.favorite, self.pages = self.check_type(
            tab, pages or params.max_pages)
        self.earliest, self.latest = self.check_date(earliest, latest)
        self.info = InfoEndpoint(params, sec_user_id, cookie)

    def check_type(self, tab: str, pages: int) -> tuple[str, bool, int]:
        if tab == "favorite":
            return self.favorite_api, True, pages
        elif tab != "post":
            self.log.warning(f"tab 参数 {tab} 设置错误，程序将使用默认值: post")
        return self.post_api, False, 99999

    def check_date(self, start: str, end: str) -> tuple[date, date]:
        return self.check_earliest(start), self.check_latest(end)

    def check_earliest(self, date_: str) -> date:
        if not date_:
            return date(2016, 9, 20)
        try:
            earliest = datetime.strptime(
                date_, "%Y/%m/%d")
            self.log.info(f"作品最早发布日期: {date_}")
            return earliest.date()
        except ValueError:
            self.log.warning(f"作品最早发布日期 {date_} 无效")
            return date(2016, 9, 20)

    def check_latest(self, date_: str) -> date:
        if not date_:
            return date.today()
        try:
            latest = datetime.strptime(date_, "%Y/%m/%d").date()
            self.log.info(f"作品最晚发布日期: {date_}")
            return latest
        except ValueError:
            self.log.warning(f"作品最晚发布日期无效 {date_}")
            return date.today()

    def run(self) -> tuple[list[dict], date, date]:
        with self.progress_object() as progress:
            task_id = progress.add_task(
                "正在获取账号主页数据", total=None)
            while not self.finished and self.pages > 0:
                progress.update(task_id)
                self.get_account_data(self.api, finished=True)
                self.early_stop()
                self.pages -= 1
                # break  # 调试代码
        self.summary_works()
        self.favorite_mode()
        return self.response, self.earliest, self.latest

    @retry
    def get_account_data(self, api: str):
        if self.favorite:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "sec_user_id": self.sec_user_id,
                "max_cursor": self.cursor,
                "min_cursor": "0",
                "whale_cut_token": "",
                "cut_version": "1",
                "count": "18",
                "publish_video_strategy_type": "2",
                "pc_client_type": "1",
                "version_code": "170400",
                "version_name": "17.4.0",
                "cookie_enabled": "true",
                "platform": "PC",
                "downlink": "10",
            }
        else:
            params = {
                "device_platform": "webapp",
                "aid": "6383",
                "channel": "channel_pc_web",
                "sec_user_id": self.sec_user_id,
                "max_cursor": self.cursor,
                "locate_query": "false",
                "show_live_replay_strategy": "1",
                "need_time_list": "0" if self.cursor else "1",
                "time_list_query": "0",
                "whale_cut_token": "",
                "cut_version": "1",
                "count": "18",
                "publish_video_strategy_type": "2",
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
            self.log.warning("获取账号作品数据失败")
            return False
        try:
            if (data_list := data["aweme_list"]) is None:
                self.log.info("该账号为私密账号，需要使用登录后的 Cookie，且登录的账号需要关注该私密账号")
                self.finished = True
            else:
                self.cursor = data['max_cursor']
                self.deal_item_data(data_list)
                self.finished = not data["has_more"]
            return True
        except KeyError:
            self.log.error(f"账号作品数据响应内容异常: {data}")
            self.finished = True
            return False

    def early_stop(self):
        """如果获取数据的发布日期已经早于限制日期，就不需要再获取下一页的数据了"""
        if not self.favorite and self.earliest > datetime.fromtimestamp(
                max(self.cursor / 1000, 0)).date():
            self.finished = True

    def favorite_mode(self):
        if not self.favorite:
            return
        info = Extractor.get_user_info(self.info.run())
        if self.sec_user_id != (s := info.get("sec_uid")):
            self.log.error(
                f"sec_user_id {self.sec_user_id} 与 {s} 不一致")
            self.generate_temp_data()
        else:
            self.response.append({"author": info})

    def generate_temp_data(self):
        temp_data = timestamp()
        self.log.warning(f"获取账号昵称失败，本次运行将临时使用 {temp_data} 作为账号昵称和 UID")
        temp_dict = {
            "author": {
                "nickname": temp_data,
                "uid": temp_data,
            }
        }
        self.response.append(temp_dict)

    def summary_works(self):
        self.log.info(f"当前账号获取作品数量: {len(self.response)}")
