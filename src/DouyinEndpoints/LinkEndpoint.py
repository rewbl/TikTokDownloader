from re import compile
from urllib.parse import urlparse, parse_qs

from src.DouyinEndpoints.ShareEndpoint import ShareEndpoint
from src.config import Parameter


class LinkEndpoint:
    # 抖音链接
    account_link = compile(
        r"\S*?https://www\.douyin\.com/user/([A-Za-z0-9_-]+)(?:\S*?\bmodal_id=(\d{19}))?")  # 账号主页链接
    account_share = compile(
        r"\S*?https://www\.iesdouyin\.com/share/user/(\S*?)\?\S*?"  # 账号主页分享链接
    )
    works_id = compile(r"\b(\d{19})\b")  # 作品 ID
    works_link = compile(
        r"\S*?https://www\.douyin\.com/(?:video|note)/([0-9]{19})\S*?")  # 作品链接
    works_share = compile(
        r"\S*?https://www\.iesdouyin\.com/share/(?:video|note)/([0-9]{19})/\S*?"
    )  # 作品分享链接
    works_search = compile(
        r"\S*?https://www\.douyin\.com/search/\S+?modal_id=(\d{19})\S*?"
    )  # 搜索作品链接
    works_discover = compile(
        r"\S*?https://www\.douyin\.com/discover\S*?modal_id=(\d{19})\S*?"
    )  # 首页作品链接
    mix_link = compile(
        r"\S*?https://www\.douyin\.com/collection/(\d{19})\S*?")  # 合集链接
    mix_share = compile(
        r"\S*?https://www\.iesdouyin\.com/share/mix/detail/(\d{19})/\S*?")  # 合集分享链接
    live_link = compile(r"\S*?https://live\.douyin\.com/([0-9]+)\S*?")  # 直播链接
    live_link_self = compile(
        r"\S*?https://www\.douyin\.com/follow\?webRid=(\d+)\S*?"
    )
    live_link_share = compile(
        r"\S*?https://webcast\.amemv\.com/douyin/webcast/reflow/\S+")

    # TikTok 链接
    works_link_tiktok = compile(
        r"\S*?https://www\.tiktok\.com/@\S+?/video/(\d{19})\S*?")  # 作品链接

    def __init__(self, params: Parameter):
        self.share = ShareEndpoint(params.logger, params.proxies, params.max_retry)

    def user(self, text: str) -> list:
        urls = self.share.run(text)
        link = [i for i in [i[0]
                            for i in self.account_link.findall(urls)] if i]
        share = self.account_share.findall(urls)
        return link + share

    def works(self, text: str) -> tuple[bool, list]:
        urls = self.share.run(text)
        if u := self.works_link_tiktok.findall(urls):
            return True, u
        link = self.works_link.findall(urls)
        share = self.works_share.findall(urls)
        account = [i for i in [i[1]
                               for i in self.account_link.findall(urls)] if i]
        search = self.works_search.findall(urls)
        discover = self.works_discover.findall(urls)
        return False, link + share + account + search + discover

    def mix(self, text: str) -> tuple:
        urls = self.share.run(text)
        share = self.works_share.findall(urls)
        link = self.works_link.findall(urls)
        search = self.works_search.findall(urls)
        discover = self.works_discover.findall(urls)
        if u := share + link + search + discover:
            return False, u
        link = self.mix_link.findall(urls)
        share = self.mix_share.findall(urls)
        return True, u if (u := link + share) else None, []

    def live(self, text: str) -> tuple:
        urls = self.share.run(text)
        if u := self.live_link.findall(urls):
            return True, u
        elif u := self.live_link_self.findall(urls):
            return True, u
        elif u := self.live_link_share.findall(urls):
            return False, self.extract_sec_user_id(u)
        return None, []

    @staticmethod
    def extract_sec_user_id(urls: list[str]) -> list[list]:
        data = []
        for url in urls:
            url = urlparse(url)
            query_params = parse_qs(url.query)
            data.append([url.path.split("/")[-1],
                         query_params.get("sec_user_id", [""])[0]])
        return data
