from unittest import TestCase

import requests

from src.StudioY.TikTok.TikTokUserInfoJson import TikTokUserInfoJson


class RapidApiClient:
    headers = {
        "X-RapidAPI-Key": "780c70b335mshfca6c6f1d5adecfp1977b1jsna4a4df21667f",
        "X-RapidAPI-Host": "tiktok-private1.p.rapidapi.com"
    }

    def get_user(self, username) -> TikTokUserInfoJson | None:
        url = "https://tiktok-private1.p.rapidapi.com/user/get-by-username"
        querystring = {"username": username}
        data = self.api_get(url, querystring).get('user_info')
        try:
            return TikTokUserInfoJson.from_json(data)
        except Exception as e:
            print(e)
            return None

    def get_posts(self, uid, sec_uid, cursor):
        url = "https://tiktok-private1.p.rapidapi.com/user/posts"
        querystring = {"user_id": uid, "sec_uid": sec_uid, "count": "30", "cursor": str(cursor)}
        data = self.api_get(url, querystring)
        return data

    def api_get(self, url, querystring):
        response = requests.get(url, headers=self.headers, params=querystring)
        return response.json()


class TikTokTest(TestCase):

    def test_api(self):
        data = RapidApiClient().get_user('saritacharrer.s')
        breakpoint()

    def test_get_posts(self):
        uid='7330736351522309162'
        sec_uid='MS4wLjABAAAAMUO3QAXA8dzE8GiaYn3RtvPGkqLVYG6bWnQkgF93Wdz8SWRlR4n77UuZWmaTn_fq'
        cursor=0
        data = RapidApiClient().get_posts(uid, sec_uid, cursor)
        breakpoint()