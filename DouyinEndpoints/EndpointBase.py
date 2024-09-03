import logging

import aiohttp
from requests import request, exceptions

from Parameter import XBogus


class Encrypter:
    @staticmethod
    def encrypt_request(params: dict, ms_token: str, number: int = 8):
        if ms_token:
            params["msToken"] = ms_token
        params["X-Bogus"] = XBogus().get_x_bogus(params, number)


class EndpointBase:

    def __init__(self, cookie: str, proxy=None):
        super().__init__()
        self.PC_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.douyin.com/",
            "Cookie": cookie
        }
        self.proxy = proxy

    def send_request(
            self,
            url: str,
            params=None,
            data=None,
            method='get',
            headers=None) -> dict | bool:
        try:
            response = request(
                method,
                url,
                params=params,
                headers=headers or self.PC_headers,
                data=data,
                proxies=self.proxy,
                verify=False)
        except Exception as e:
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

    async def send_request_async(
            self,
            url: str,
            params=None,
            method='get',
            data=None,
            headers=None) -> dict | bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                        method,
                        url,
                        params=params,
                        data=data,
                        proxy=self.proxy.get('http',''),
                        headers=headers or self.PC_headers) as response:
                    try:
                        return await response.json()
                    except Exception as e:
                        logging.error(f"Error parsing JSON response: {e}")
                        return False
        except Exception as e:
            logging.error(f"Request failed: {e}")
            return False
