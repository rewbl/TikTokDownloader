import asyncio
import os
import shutil
import time

import urllib3

from app.BookmarkDownloader import async_bookmark, download_recent_videos
urllib3.disable_warnings()


async def main():
    accounts = ['DF1', 'DF2', 'J1', 'J2', 'J3', 'BH1', 'DF3', 'DF4', 'DF5', 'BL1', 'DF6','BH2']
    accounts = ['DF1', 'DF2', 'BH1', 'DF3', 'DF4', 'DF5', 'BL1', 'DF6','BH2']
    # accounts = ['DF5']
    while True:
        start_time = time.time()

        for account_code in accounts:
            print(f'\r\n{account_code} =====================================')
            try:
                await async_bookmark(account_code)
                download_recent_videos(account_code, True, 'temp')
            except Exception as e:
                print(e)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time: {execution_time} seconds")
        sleep_time = max(600 - execution_time, 0)
        await asyncio.sleep(sleep_time)

if __name__ == '__main__':
    # Define the directory name
    dir_name = 'temp'

    # Check if the directory exists
    if os.path.exists(dir_name):
        # Delete the directory
        shutil.rmtree(dir_name)

    # Create the directory
    os.makedirs(dir_name)
    asyncio.run(main())