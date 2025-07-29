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


async def send_slack_notification(name, message=None, blocks=None) -> bool:
    try:
        response = await client.chat_postMessage(
            channel=notification_channel_ids[name],
            text=str(message),
            blocks=blocks)
        return True
    except SlackApiError as e:
        print(f"Error posting message: {e.response['error']}")
        return False


async def download_video_to_temp(video_url: str, nickname: str) -> str:
    """
    下载视频到临时文件
    """
    try:
        # 创建临时文件
        time_str = datetime.now().strftime("%d_%H_%M_%S")
        filename = f'{nickname[:30]}-{time_str}.mp4'
        filename = re.sub(r'[\\/*?:"<>|#\n\r]', '', filename)
        
        temp_dir = tempfile.gettempdir()
        temp_file_path = os.path.join(temp_dir, filename)
        
        print(f"开始下载视频: {temp_file_path}")
        
        # 下载视频
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status == 200:
                    with open(temp_file_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                    print(f"视频下载完成: {temp_file_path}")
                    return temp_file_path
                else:
                    print(f"下载视频失败，状态码: {response.status}")
                    return None
    except Exception as e:
        print(f"下载视频时发生错误: {e}")
        return None


async def send_slack_notification_with_video(name: str, message: str = None, blocks=None, 
                                           video_url: str = None, nickname: str = None) -> bool:
    """
    发送带视频附件的Slack通知
    """
    temp_file_path = None
    try:
        # 发送消息
        response = await client.chat_postMessage(
            channel=notification_channel_ids[name],
            text=str(message),
            blocks=blocks
        )
        
        # 如果有视频URL，下载并上传
        if video_url and nickname:
            temp_file_path = await download_video_to_temp(video_url, nickname)
            
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    # 上传文件
                    with open(temp_file_path, 'rb') as file:
                        upload_response = await client.files_upload_v2(
                            channel=notification_channel_ids[name],
                            file=file,
                            filename=os.path.basename(temp_file_path),
                            title=f"视频: {nickname}",
                            initial_comment="视频附件"
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
