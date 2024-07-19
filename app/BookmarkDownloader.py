import os
import re
from unittest import IsolatedAsyncioTestCase

from DouyinEndpoints.AwemeCollectionPrivateApi import AwemeCollection
from StudioY.DouyinSession import DouyinSession
from StudioY.StudioYClient import StudioYClient
from StudioY.SyncBookmarks import AwemeCollectionRecipient
from datetime import datetime

client = StudioYClient()
Local_Temp_Folder = 'C:/SourceCode/TikTokDownloader'
class S3VideoClient:
    def __init__(self):
        self.bucket_name = "douyin-videos"
        self.endpoint_url = "http://192.168.196.226:9000"  # Assuming default MinIO port
        self.access_key = "GeYuSJwiCmdlgTSA84xE"
        self.secret_key = "wci2U9cHzxp17JrvRmaEfRO4sUxeQX1KOeugGuRk"

        self.s3_client = boto3.client('s3',
                                      endpoint_url=self.endpoint_url,
                                      aws_access_key_id=self.access_key,
                                      aws_secret_access_key=self.secret_key,
                                      region_name='us-east-1')  # Default region can be changed as needed

    def save_file_to_s3(self, local_file, s3_file) -> bool:

        try:
            with open(local_file, 'rb') as f:
                self.s3_client.upload_fileobj(f, self.bucket_name, s3_file)
            # os.remove(local_file)  # Remove the file after successful upload
            return True
        except:
            return False

async def async_bookmark(account_code):
    session = DouyinSession(account_code)
    session.load_session()
    collection = AwemeCollection(AwemeCollectionRecipient(session.account_id), session)
    await collection.load_full_list()


def _create_filename(v):
    author = v['douyinUser']['nickname']
    auther = author[:10]
    time = datetime.fromtimestamp(v['createTime'])
    time_str = f'{time.month}月{time.day}日 {time.hour}时{time.minute}分'
    caption = v['caption'][:40]
    awemeId = v['awemeId']

    filename = f"{time_str}-【{author}】-{caption}-{awemeId}.mp4"
    filename = re.sub(r'[\\/*?:"<>|#\n\r]', '', filename)
    return filename


def download_recent_videos(short_code, save_to_s3=False, root_folder=Local_Temp_Folder):
    folder = short_code
    if not os.path.exists(f'{root_folder}/{folder}'):
        os.makedirs(f'{root_folder}/{folder}')

    result = client.get_account_id_by_short_code(short_code)
    if not result['isSuccess']:
        return

    account_id = result['data']
    start_minutes_offset = 10 * 60
    vs = client.get_pending_videos(account_id, start_minutes_offset, False)
    for v in vs["data"]:
        url = v["bestBitRateUrl"]
        filename = _create_filename(v)
        download_success = False
        for i in range(3):
            try:
                client.download_video(url, f'{root_folder}/{folder}/{filename}')
                download_success = True
                break
            except Exception as e:
                print(e)
        if not download_success:
            continue
        if save_to_s3:
            S3VideoClient().save_file_to_s3(f'{root_folder}/{folder}/{filename}', f'{folder}/{filename}')
            print(f'Uploaded to S3: {folder}/{filename}')
        client.set_downloaded(account_id, v["id"])


class TestSyncAndDownload(IsolatedAsyncioTestCase):
    async def test_sync_bookmark(self):
        accounts= ['DF1', 'DF2', 'J1', 'J2', 'J3', 'BH1', 'DF3', 'DF4', 'DF5']
        accounts=['BL1']
        for account_code in accounts:
            print(f'\r\n{account_code} =====================================')

            await async_bookmark(account_code)
            download_recent_videos(account_code, True)


import unittest
import boto3
from botocore.exceptions import NoCredentialsError, ClientError


class TestMinioS3Operations(unittest.TestCase):
    def setUp(self):
        """Set up the MinIO S3 client."""
        self.bucket_name = "douyin-videos"
        self.endpoint_url = "http://192.168.196.226:9000"  # Assuming default MinIO port
        self.access_key = "GeYuSJwiCmdlgTSA84xE"
        self.secret_key = "wci2U9cHzxp17JrvRmaEfRO4sUxeQX1KOeugGuRk"

        self.s3 = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1'  # Region does not matter in MinIO but parameter is required
        )

        # Check if the bucket already exists and create it if it doesn't
        try:
            self.s3.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                raise

    def test_write_and_read_file(self):
        """Test writing a file to MinIO and reading it back."""
        object_name = 'testfile.txt'
        content = b'Hello MinIO!'

        # Write the file
        self.s3.put_object(Bucket=self.bucket_name, Key=object_name, Body=content)

        # Read the file back
        result = self.s3.get_object(Bucket=self.bucket_name, Key=object_name)
        data = result['Body'].read()

        # Check if the content matches
        self.assertEqual(data, content)

    def tearDown(self):
        """Clean up test environment; delete created objects."""
        try:
            # Delete the object
            self.s3.delete_object(Bucket=self.bucket_name, Key='testfile.txt')
            # Optionally, delete the bucket if you want to clean up completely:
            # self.s3.delete_bucket(Bucket=self.bucket_name)
        except NoCredentialsError:
            print("Credentials not available")
