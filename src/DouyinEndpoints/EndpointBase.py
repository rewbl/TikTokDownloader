from requests import request, exceptions

from src.Infrastructure.custom import wait
from src.Infrastructure.encrypt import XBogus
from src.config.RuntimeParameters import RuntimeCoreParameters


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
        self.response= []

    @staticmethod
    def init_headers(headers: dict) -> tuple:
        return (headers | {
            "Referer": "https://www.douyin.com/", },
                {"User-Agent": headers["User-Agent"]})




class EndpointBase(EndpointConst):

    def __init__(self, cookie: str):
        super().__init__()
        self.PC_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Cookie": cookie,
        }

    def send_request(
            self,
            url: str,
            params=None,
            data=None,
            method='get',) -> dict | bool:

        try:
            response = request(
                method,
                url,
                params=params,
                headers=self.PC_headers,
                data=data,
                verify=False)
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


