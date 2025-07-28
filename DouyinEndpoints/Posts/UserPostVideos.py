from typing import List

from StudioY.FavoriteVideoDto import FavoriteVideoDto


class UserPostVideos:
    sec_user_id: str
    name: str
    existing_videos: dict
    remote_video_folder: str

    def __init__(self, name, sec_user_id, remote_video_folder=None):
        self.name = name
        self.sec_user_id = sec_user_id
        self.remote_video_folder = remote_video_folder
        self.existing_videos = {}

    def update(self, videos) -> List[FavoriteVideoDto]:
        new_videos = []
        initial_count = len(self.existing_videos)
        for video in videos:
            if video.AwemeId in self.existing_videos:
                self.existing_videos[video.AwemeId] = video
                continue
            new_videos.append(video)
            self.existing_videos[video.AwemeId] = video

        # return new_videos
        return new_videos if initial_count else []
