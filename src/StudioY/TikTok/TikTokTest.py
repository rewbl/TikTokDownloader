from unittest import TestCase

import requests
from requests import request

from src.DouyinEndpoints.EndpointBase import Encrypter

cookie = '_ttp=2MYJvt2pN7OZmPqz21Crv3OQi0U; tt_csrf_token=3zgtMKET-3NGszpnqQO5v2DFHCloYwPyWGR8; cookie-consent={%22ga%22:true%2C%22af%22:true%2C%22fbp%22:true%2C%22lip%22:true%2C%22bing%22:true%2C%22ttads%22:true%2C%22reddit%22:true%2C%22hubspot%22:true%2C%22version%22:%22v10%22}; tiktok_webapp_theme=light; odin_tt=3308243aafa5b1ae701e533c303b41913c2a1ae913e0fd96d49114498ba3a474009f64a853881daf8ad4438244ae58ec8ada3d507f09198d7b05043e481578535428cad6a32d19534c42a004481b356e; s_v_web_id=verify_lq7f7x9g_FNE66wFk_sGJs_4cdU_ARyx_di8PoOZZs0qx; passport_csrf_token=71c89612011cf1a853180cbaee16ac89; passport_csrf_token_default=71c89612011cf1a853180cbaee16ac89; csrfToken=hOFQkpnW-icEJGyVDpisbeiZjsJ_HaQgyXds; tt_chain_token=aDcc9U5Jqzi9l5PXKvOWQg==; ak_bmsc=FF549C47088B65A6B8F7BE6305CF521C~000000000000000000000000000000~YAAQHKEkFxeLIEGOAQAASGiORRfxDF2EObRFtJdXNaSxR0u23VfyaQ5n4oJI/42DfCeJqmCpUlug3KXVAQjdkQL0S+jmIvHZRc6Enfyr9ug/egGk8tX+s1JZUty8Zpz/VHRjyoq3zsMjC5azir+tptQ+7C1k0Yz62ovM/4bI/y20CYe0TMzFk2aRMxDeh66J8HzuXeqvVVQGHd3IE2w97dwCTpB592ELLJPx4JllHZthOhh6Q3X68LXBM1GqsvtABhjHnbh+FMNY3OV/R5pepSNrbuudS/v67SLAf6nFoFieqgDvePJcE1ecUSpfP6N187HP9X2A7SYPP4xmIpWEFbtxKC8d2jMXIiGsrsR7YVz6pXhaoE3TdCBLtHvUziIFRaWtsxph; multi_sids=6828224526217774085%3A0283f83bdaccca6da5bb49c6b75fc0ca; cmpl_token=AgQQAPNSF-RO0o78VKD74N08_7u2e6BI_6IaYNCcLQ; uid_tt=812e3b42b46e0a8f4705326d33d0fbc30103255d09eb8f3a7f89d32fc738b620; uid_tt_ss=812e3b42b46e0a8f4705326d33d0fbc30103255d09eb8f3a7f89d32fc738b620; sid_tt=0283f83bdaccca6da5bb49c6b75fc0ca; sessionid=0283f83bdaccca6da5bb49c6b75fc0ca; sessionid_ss=0283f83bdaccca6da5bb49c6b75fc0ca; store-idc=useast5; store-country-code=us; store-country-code-src=uid; tt-target-idc=useast5; tt-target-idc-sign=w9y0Vn9EK4wffEnm0wkRa3k_3qI_wWEP96_woVp7HWyYfV9zp_zqvXFnT4Gf_BV734Gt2sYYRaZ_dgfnS9zYRhleoL-2U04dAcHxDOV0EJvEB0ose-bAzf8gJ9LKUYjDzVwB5jehocFGHWmxSsuX__ivStVZyiF8jm10ttAagD1ZqwMGuLynqwzCVLr8xRUjkvrOsfyo701u_UJ23ILmHpugAiEeiZ-ZtWfCibW0UIOhHxz3wWDcda0iVauiuEppL9Q0ZSPBPttrn0fHGxSApM-U9Z2X68obSAsGpnS7U6xayQ5Bk8nTkglVHHzXM1SVK34oBCIuLKsI78cCcaS19l3pzYt4dgx7sX_kU9oIH9CS6zLFUlaLLwCpb6QL9HlEypSstkRln13zXT3JMrQ4liQkFrXb-3YUqBTvM2M2nuAwbZqGHX-8goJ-xOPs4Etg0AIGluk2v-5ydDjQpI6vIjLmVrBtBcZ6GitVvEryEX_na-h-e5o1d_NSzk-0PUHN; last_login_method=handle; sid_guard=0283f83bdaccca6da5bb49c6b75fc0ca%7C1710564097%7C15551996%7CThu%2C+12-Sep-2024+04%3A41%3A33+GMT; sid_ucp_v1=1.0.0-KDI4MTZiMWE3MjU3MDgyNjU0ZmFlYTFmNDVkOWZmYmM5NTQ0ODZjMDYKGAiFiMie98Cu4V4QgcbUrwYYsws4BEDqBxAEGgd1c2Vhc3Q1IiAwMjgzZjgzYmRhY2NjYTZkYTViYjQ5YzZiNzVmYzBjYQ; ssid_ucp_v1=1.0.0-KDI4MTZiMWE3MjU3MDgyNjU0ZmFlYTFmNDVkOWZmYmM5NTQ0ODZjMDYKGAiFiMie98Cu4V4QgcbUrwYYsws4BEDqBxAEGgd1c2Vhc3Q1IiAwMjgzZjgzYmRhY2NjYTZkYTViYjQ5YzZiNzVmYzBjYQ; passport_fe_beating_status=true; bm_sv=4DFDCA977E3FCB173C56A4CEF1D2CE14~YAAQCaEkF0KhLT2OAQAA+V6xRRcADnJCsc+CawD34SjJgICawTOZTn9krJ+uq+MNR6QTrlXEljW5kJYXjhk8k26tAzByJJr5XnkGHNY9cV2OBovDli9uJjUviDeCIjG54aP2kLp679MDfICWx0vr0BpMC3U4wpCK9XrNVQQpftLTi8CehEI7N8L9+EjpNw9lA40tnsv2Mnl16zzwcGwQ1vHgTtInb8JtWzjU4cDtI+s4uEDT3yYJMQnrN5vZoQcq~1; ttwid=1%7CkqCKNr0WlzX7xPvflppGD3YDhQX7qUpmO-joKgCQuVM%7C1710566236%7C14e42cae54ae12bcf039c8aef84ccbe9f5926b03d7b8ec24b5bf708fae71e5d5; msToken=SbtT3uVlRL3yZIBOucR8Rf1C0pHWdIN44Q15vaV9Oq8437Prrt_p5Xzuuwb-zXpAmKf0NZl1Or2PAUSaVP5rQaSY4-k9Whnvafz-G4D3A41tBJy2jLGdpSAY4a3kY1GCkN-4jz4W7yS5iFqn; perf_feed_cache={%22expireTimestamp%22:1710738000000%2C%22itemIds%22:[%227339147258513919264%22%2C%227319486297121312005%22%2C%227341413558720384302%22]}; msToken=wBvDcYBFNASTr-3q4y9dyX9S3zQ559ro--HFz2FcB6tg8GoewZUhtCipx6Z_9J11noUoCxbO2bHb2Iw_fDtcHDSzJ1FDiXHLS46qTOI1ly7yoVbf-M7zSsgSR6pUG8rnAU1K2uY='


class TikTokTest(TestCase):
    def test(self):
        url ='https://www.tiktok.com/api/explore/item_list/?aid=1988&categoryType=119&count=16'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Referer': 'https://www.tiktok.com',
            'Cookie': cookie
        }
        response = requests.get(url, headers=headers, verify=False)
        print(response.json())



    def test2(self):
        msToken='wBvDcYBFNASTr-3q4y9dyX9S3zQ559ro--HFz2FcB6tg8GoewZUhtCipx6Z_9J11noUoCxbO2bHb2Iw_fDtcHDSzJ1FDiXHLS46qTOI1ly7yoVbf-M7zSsgSR6pUG8rnAU1K2uY='
        api_params = {
            "WebIdLastTime": "1710564093",
            "aid": "1988",
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_name": "Mozilla",
            "browser_online": "true",
            "browser_platform": "Win32",
            "browser_version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "channel": "tiktok_web",
            "cookie_enabled": "true",
            "count": "35",
            "coverFormat": "2",
            "cursor": "1710473119000",
            "device_id": "7339230529303594528",
            "device_platform": "web_pc",
            "focus_state": "false",
            "from_page": "user",
            "history_len": "8",
            "is_fullscreen": "false",
            "is_page_visible": "true",
            "language": "en",
            "os": "windows",
            "priority_region": "US",
            "referer": "",
            "region": "DE",
            "screen_height": "2160",
            "screen_width": "3840",
            "secUid": "MS4wLjABAAAApEbAzLsl3uVGmWPeCcK0xfFtGutTrSQZTkQPyjvPuxPNdh3GZAmVWfgJTj8tjaC8",
            "tz_name": "America/Los_Angeles",
            "verifyFp": "verify_lq7f7x9g_FNE66wFk_sGJs_4cdU_ARyx_di8PoOZZs0qx",
            "webcast_language": "en",
        }
        url = 'https://www.tiktok.com/api/post/item_list/'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com',
            'Cookie': cookie
        }

        Encrypter.encrypt_request(api_params, msToken, 4)
        response =request(
            'get',
            url,
            params=api_params,
            headers=headers,
            verify=False)
        data = response.json()
        breakpoint()