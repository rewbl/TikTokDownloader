from unittest import TestCase, IsolatedAsyncioTestCase
import asyncio
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

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

SB = ''
client = AsyncWebClient(token=SB)


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


class Test(IsolatedAsyncioTestCase):
    async def test_send_slack_notification(self):
        self.assertTrue(await send_slack_notification('general', 'Hello, this is a async test message!'))
#xoxb-4202093198051-7466607161910-xKUIUNtXsvpCR7eNjasPK3yn