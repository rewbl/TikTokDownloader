from unittest import IsolatedAsyncioTestCase

from src.DouyinEndpoints.AwemeCollectionPrivateApi import AwemeCollection
from src.StudioY.DouyinSession import DouyinSession
from src.StudioY.StudioYClient import StudioYClient
from src.StudioY.SyncBookmarks import AwemeCollectionRecipient

client = StudioYClient()


async def async_bookmark(account_code):
    session = DouyinSession(account_code)
    session.load_session()
    collection = AwemeCollection(AwemeCollectionRecipient(session.account_id), session)
    await collection.load_full_list()

def download_recent_videos(short_code):
    folder ={
        "DF1": "DF1",
        "DF2": "DF2",
        "J1": "J1",
        "BH1": "BH1",
        "BL1": "BL1"
    }[short_code]
    result = client.get_account_id_by_short_code(short_code)
    if not result['isSuccess']:
        return

    account_id = result['data']
    start_minutes_offset = 24 * 60
    vs = client.get_pending_videos(account_id, start_minutes_offset)
    for v in vs["data"]:
        url = v["bestBitRateUrl"]
        filename = f"{v['awemeId']}.mp4"
        for i in range(3):
            try:
                client.download_video(url, f'C:/SourceCode/TikTokDownloader/{folder}/{filename}')
                break
            except Exception as e:
                print(e)
        client.set_downloaded(account_id, v["id"])




class TestSyncAndDownload(IsolatedAsyncioTestCase):
    async def test_sync_bookmark(self):
        account_code = 'BL1'
        await async_bookmark(account_code)
        download_recent_videos(account_code)
