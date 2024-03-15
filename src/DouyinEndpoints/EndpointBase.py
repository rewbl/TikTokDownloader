from urllib.parse import urlencode, unquote, quote

from requests import request, exceptions
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn

from src.Infrastructure.custom import wait, PROGRESS
from src.Infrastructure.encrypt import XBogus
from src.StudioY.DouyinSession import DouyinSession
from src.config import RuntimeParameters


class Encrypter:
    @staticmethod
    def encrypt_request(params: dict, ms_token: str, number: int = 8):
        if ms_token:
            params["msToken"] = ms_token
        params["X-Bogus"] = XBogus().get_x_bogus(params, number)


class EndpointConst:
    reply_tiktok_api = "https://www.tiktok.com/api/comment/list/reply/"  # 评论回复API
    comment_tiktok_api = "https://www.tiktok.com/api/comment/list/"  # 评论API
    related_tiktok_api = "https://www.tiktok.com/api/related/item_list/"  # 猜你喜欢API
    user_tiktok_api = "https://www.tiktok.com/api/user/detail/"  # 账号数据API
    home_tiktok_api = "https://www.tiktok.com/api/post/item_list/"  # 发布页API
    recommend_api = "https://www.tiktok.com/api/recommend/item_list/"  # 推荐页API
    following_api = "https://www.douyin.com/aweme/v1/web/user/following/list/"  # 关注列表API
    history_api = "https://www.douyin.com/aweme/v1/web/history/read/"  # 观看历史API
    follow_api = "https://www.douyin.com/aweme/v1/web/follow/feed/"  # 关注账号作品推荐API
    familiar_api = "https://www.douyin.com/aweme/v1/web/familiar/feed/"  # 朋友作品推荐API
    spotlight_api = "https://www.douyin.com/aweme/v1/web/im/spotlight/relation/"  # 关注账号API
    feed_api = "https://www.douyin.com/aweme/v1/web/tab/feed/"  # 推荐页API
    mix_list_api = "https://www.douyin.com/aweme/v1/web/mix/listcollection/"  # 合集列表API
    Phone_headers = {
        'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)'
                      '+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'}

    cookie: str = None

    def __init__(self):
        self.response = []


    def _get_ms_token(self):
        return 'TJ0BxOmRkvHgQkh0-vrWD0ZFwo9AoSufF6kEt_3u4oyU6LS-BjrlVanNfd5cMZc5fUpFWccrUSYI8go_NZXF46yEN7urBb6RVtR1t4veNWnbFi76ejGAQjOZxhflwg4='
        if isinstance(self.cookie, dict) and "msToken" in self.cookie:
            return self.cookie["msToken"]

    def deal_url_params(self, params: dict, number=8):
        Encrypter.encrypt_request(params, self._get_ms_token(), number)

    def move_list_to_response(
            self,
            data: list[dict],
            start: int = None,
            end: int = None):
        if not data:
            return

        for i in data[start:end]:
            self.response.append(i)


class EndpointBase(EndpointConst):

    def __init__(self, params: DouyinSession, cookie: str = None):
        super().__init__()
        self.log = params.logger
        self.console = params.console
        self.proxies = params.proxies
        self.max_retry = 5
        self.timeout = 10
        self.cursor = 0
        self.finished = False
        self.session: DouyinSession = params

    @property
    def cookies(self):
        return self.session.cookie_jar

    def send_request(
            self,
            url: str,
            params=None,
            method='get',
            headers=None,
            **kwargs) -> dict | bool:
        self.session.update_cookie_header()
        try:
            response = request(
                method,
                url,
                params=params,
                proxies=self.proxies,
                timeout=self.timeout,
                headers=self.session.headers,
                # cookies=self.session.cookie_jar,
                verify=False,
                **kwargs)
            wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            return False
        except exceptions.ReadTimeout:
            return False
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                # self.log.warning(f"响应内容不是有效的 JSON 格式：{response.text}")
                ...
            else:
                # self.log.warning("响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie")
                ...
            return False

    def progress_object(self):
        return Progress(
            TextColumn(
                "[progress.description]{task.description}",
                style=PROGRESS,
                justify="left"),
            "•",
            BarColumn(
                bar_width=20),
            "•",
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )


class EndpointBaseY:
    Phone_headers = {
        'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)'
                      '+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36'}
    # 抖音 API
    mix_list_api = "https://www.douyin.com/aweme/v1/web/mix/listcollection/"  # 合集列表API
    feed_api = "https://www.douyin.com/aweme/v1/web/tab/feed/"  # 推荐页API
    spotlight_api = "https://www.douyin.com/aweme/v1/web/im/spotlight/relation/"  # 关注账号API
    familiar_api = "https://www.douyin.com/aweme/v1/web/familiar/feed/"  # 朋友作品推荐API
    follow_api = "https://www.douyin.com/aweme/v1/web/follow/feed/"  # 关注账号作品推荐API
    history_api = "https://www.douyin.com/aweme/v1/web/history/read/"  # 观看历史API
    following_api = "https://www.douyin.com/aweme/v1/web/user/following/list/"  # 关注列表API

    # TikTok API
    recommend_api = "https://www.tiktok.com/api/recommend/item_list/"  # 推荐页API
    home_tiktok_api = "https://www.tiktok.com/api/post/item_list/"  # 发布页API
    user_tiktok_api = "https://www.tiktok.com/api/user/detail/"  # 账号数据API
    related_tiktok_api = "https://www.tiktok.com/api/related/item_list/"  # 猜你喜欢API
    comment_tiktok_api = "https://www.tiktok.com/api/comment/list/"  # 评论API
    reply_tiktok_api = "https://www.tiktok.com/api/comment/list/reply/"  # 评论回复API

    def __init__(self, params: RuntimeParameters, cookie: str = None):
        self.PC_headers, self.black_headers = params.headers
        self.log = params.logger
        self.xb = params.xb
        self.console = params.console
        self.proxies = params.proxies
        self.max_retry = params.max_retry
        self.timeout = params.timeout
        self.cookie = params.cookie
        self.cursor = 0
        self.response = []
        self.finished = False
        self.__set_temp_cookie(cookie)

    def send_request(
            self,
            url: str,
            params=None,
            method='get',
            headers=None,
            **kwargs) -> dict | bool:
        try:
            response = request(
                method,
                url,
                params=params,
                proxies=self.proxies,
                timeout=self.timeout,
                headers=headers or self.PC_headers,
                verify=False,
                **kwargs)
            wait()
        except (
                exceptions.ProxyError,
                exceptions.SSLError,
                exceptions.ChunkedEncodingError,
                exceptions.ConnectionError,
        ):
            self.log.warning(f"网络异常，请求 {url}?{urlencode(params)} 失败")
            return False
        except exceptions.ReadTimeout:
            self.log.warning(f"网络异常，请求 {url}?{urlencode(params)} 超时")
            return False
        try:
            return response.json()
        except exceptions.JSONDecodeError:
            if response.text:
                self.log.warning(f"响应内容不是有效的 JSON 格式：{response.text}")
            else:
                self.log.warning("响应内容为空，可能是接口失效或者 Cookie 失效，请尝试更新 Cookie")
            return False

    def deal_url_params(self, params: dict, number=8):
        self.__add_ms_token(params)
        params["X-Bogus"] = self.xb.get_x_bogus(params, number)

    def __add_ms_token(self, params: dict):
        if isinstance(self.cookie, dict) and "msToken" in self.cookie:
            params["msToken"] = self.cookie["msToken"]

    def deal_item_data(
            self,
            data: list[dict],
            start: int = None,
            end: int = None):
        if not data:
            return

        for i in data[start:end]:
            self.response.append(i)

    def progress_object(self):
        return Progress(
            TextColumn(
                "[progress.description]{task.description}",
                style=PROGRESS,
                justify="left"),
            "•",
            BarColumn(
                bar_width=20),
            "•",
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        )

    def __set_temp_cookie(self, cookie: str):
        if cookie:
            self.PC_headers["Cookie"] = cookie
