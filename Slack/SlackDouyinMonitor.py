from unittest import TestCase, IsolatedAsyncioTestCase
import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
import certifi
import base64
import os
import tempfile
import aiohttp
from datetime import datetime
import re
import requests

from StudioY.FavoriteVideoDto import FavoriteVideoDto, DouyinAuthorDto

# Name: general, ID: C045HJ72M9D
# Name: random, ID: C045Y582RV0
# Name: spk, ID: C0460JKNA04
# Name: marketing, ID: C04SG6GL3FW
# Name: purchase, ID: C04SG6HA0MS
# Name: ui-design, ID: C04SUJG9P97
# Name: payment, ID: C04T3CWFUUQ
# Name: woocommerce-tech-support, ID: C04T5KRCAE4
# Name: tax, ID: C04U9ME0M2M
# Name: products, ID: C05D8H7FKK4
# Name: marketing-youtube, ID: C05L20PMNSC
# Name: suzewig, ID: C079S9J1MS6
# Name: douyin-monitor-bot-general, ID: C07DQKR54FQ
# Name: douyin-monitor-bot-vivian, ID: C07E01R3MQB
# Name: douyin-monitor-bot-heqiang, ID: C07E02XE2RZ
# Name: douyin-monitor-bot-bohai, ID: C07ENV8L5CG
# Replace with your actual token
notification_channel_ids = {
    'general': 'C07DQKR54FQ',
    'vivian': 'C07E01R3MQB',
    'heqiang': 'C07E02XE2RZ',
    'bohai': 'C07ENV8L5CG',
}

SB_b64 = 'eG94Yi00MjAyMDkzMTk4MDUxLTc0NjY2MDcxNjE5MTAtMVM1RjNZTWxWQWk0ZEFic2FFV0Ric21T'

SB = base64.b64decode(SB_b64).decode()
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
client = AsyncWebClient(token=SB, ssl=ssl_context)

# 同步版本的Slack客户端
sync_client = WebClient(token=SB, ssl=ssl_context)


async def list_channels():
    try:
        response = await client.conversations_list()
        for channel in response['channels']:
            print(f"Name: {channel['name']}, ID: {channel['id']}")
    except SlackApiError as e:
        print(f"Error listing channels: {e.response['error']}")


# Define the channel ID and message text
channel_id = 'C07E02XE2RZ'  # Replace with your channel ID
message_text = 'Hello, this is a message from the bot! Here is a link http://www.cnn.com'


def download_video(video_url: str) -> str:
    try:
        # 创建临时文件
        time_str = datetime.now().strftime("%d_%H_%M_%S")
        filename = f'{time_str}.mp4'

        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)
        
        print(f"开始下载视频: {temp_file_path}")
        
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(temp_file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"视频下载完成: {temp_file_path}")
            return temp_file_path
        else:
            print(f"下载视频失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"下载视频时发生错误: {e}")
        return None


def send_slack_notification_with_video(name: str, message: str = None, blocks=None,
                                       video_url: str = None) -> bool:
    temp_file_path = None
    try:
        response = sync_client.chat_postMessage(
            channel=notification_channel_ids[name],
            text=str(message),
            blocks=blocks
        )
        
        if not video_url:
            return True

        temp_file_path = download_video(video_url)
        if not temp_file_path or not os.path.exists(temp_file_path):
            return False

        try:
            with open(temp_file_path, 'rb') as file:
                upload_response = sync_client.files_upload_v2(
                    channel=notification_channel_ids[name],
                    file=file,
                    filename=os.path.basename(temp_file_path),
                    initial_comment="视频附件",
                    thread_ts=response['ts']  # 作为回复发送
                )
            print(f"视频附件上传成功: {upload_response['file']['name']}")
        except SlackApiError as e:
            print(f"上传视频附件失败: {e.response['error']}")
        except Exception as e:
            print(f"上传视频附件时发生错误: {e}")
        
        return True
        
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return False
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"临时文件已清理: {temp_file_path}")
            except Exception as e:
                print(f"清理临时文件失败: {e}")


class TestNotification(TestCase):
    def test_send_notification(self):
        video = FavoriteVideoDto(
            Author=DouyinAuthorDto(
                Uid="test_uid_123",
                SecUid="test_sec_uid_456",
                Nickname="测试用户x",
                AvatarUrl="https://example.com/avatar.jpg"
            ),
            AwemeId="test_aweme_id_789",
            Caption="测试视频标题",
            Description="测试视频描述",
            CoverUrl="https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png",
            BestBitRateUrl="https://api.amemv.com/aweme/v1/play/?video_id=v0d00fg10000d23lcdvog65nc92u9uu0&line=1&file_id=f2291422aa174c5b8d9c48347357e656&sign=475c6fd97307c09832b7a49d8efb3b39&is_play_url=1&source=PackSourceEnum_PUBLISH"
        )
        text, blocks = video.notification_summary()
        send_slack_notification_with_video(
            name='general',
            message=text,
            blocks=blocks,
            video_url=video.BestBitRateUrl
        )
