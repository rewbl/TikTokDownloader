from src.StudioY.StudioYClient import StudioYClient

client = StudioYClient()


def download_recent_videos(short_code, folder):
    result = client.get_account_id_by_short_code(short_code)
    if not result['isSuccess']:
        return

    account_id = result['data']
    start_minutes_offset = 100
    vs = client.get_pending_videos(account_id, start_minutes_offset)
    for v in vs["data"]:
        url = v["bestBitRateUrl"]
        filename = f"{v['awemeId']}.mp4"
        for i in range(3):
            try:
                client.download_video(url, f'z:/video/StudioY/{folder}/{filename}')
                break
            except Exception as e:
                print(e)
        client.set_downloaded(account_id, v["id"])


shortcodes = [
    # ['DF1', "DF1"],
    # ['DF2', "DF2"],
    ['J1', "J1"],
    # ['BH1', "BH1"],
]
for shortcode, folder_name in shortcodes:
    download_recent_videos(shortcode, folder_name)
