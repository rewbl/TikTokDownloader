from re import compile

from requests import request, exceptions

from src.Infrastructure.custom import wait
from src.Infrastructure.tools import retry


class ShareEndpoint:
    share_link = compile(
        r"\S*?(https://v\.douyin\.com/[^/\s]+)\S*?")
    share_link_tiktok = compile(
        r"\S*?(https://vm\.tiktok\.com/[^/\s]+)\S*?")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome"
                      "/116.0.0.0 Safari/537.36", }

    def __init__(self, logger, proxies: dict, max_retry=10):
        self.max_retry = max_retry
        self.log = logger
        self.proxies = proxies

    def run(self, text: str) -> str:
        if (u := self.share_link.findall(text)) or (
                u := self.share_link_tiktok.findall(text)):
            return " ".join(self.get_url(i) for i in u)
        return text

    @retry
    def get_url(self, url: str) -> str:
        try:
            response = request(
                "get",
                url,
                timeout=10,
                proxies=self.proxies,
                headers=self.headers, )
            wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
                exceptions.ReadTimeout,
        ):
            self.log.warning(f"分享链接 {url} 请求数据失败")
            return ""
        return response.url
