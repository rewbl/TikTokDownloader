from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

from PostMonitor.douyin_post_service import NotionDouyinPostService
from Slack.SlackDouyinMonitor import send_slack_notification_with_video
from StudioY.FavoriteVideoDto import FavoriteVideoDto

_thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="video_processor")


async def process_new_video(video: FavoriteVideoDto, account_page_id: str, account_name: str = None, slack_channel: str = 'vivian'):
    future = _thread_pool.submit(_handle_new_video_sync, video, account_page_id, account_name, slack_channel)
    print(f"已提交新视频处理任务到线程池: {video.AwemeId}")
    return future


def _handle_new_video_sync(video: FavoriteVideoDto, account_page_id: str, account_name: str, slack_channel: str):

    post_service = NotionDouyinPostService()

    try:
        # 1. 创建Notion记录
        page_id = post_service.create_post_from_video(video, account_page_id, account_name)

        if page_id:
            print(f"成功创建Notion记录: {video.AwemeId}")
        else:
            print(f"创建Notion记录失败: {video.AwemeId}")

        # 2. 发送Slack通知（即使失败也不影响主流程）
        try:
            text, blocks = video.notification_summary()
            # 直接使用同步版本的Slack通知
            success = send_slack_notification_with_video(slack_channel, text, blocks, video.BestBitRateUrl)

            if success:
                print(f"成功发送Slack通知: {video.AwemeId}")
            else:
                print(f"发送Slack通知失败: {video.AwemeId}")
        except Exception as slack_error:
            print(f"Slack通知异常: {slack_error}")
            # Slack失败不影响主流程

    except Exception as e:
        print(f"处理新视频失败: {e}")
        import traceback
        traceback.print_exc()
