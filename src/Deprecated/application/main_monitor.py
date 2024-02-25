from src.application.TikTokCLI import TikTokCLI

__all__ = ["Monitor"]


class Monitor(TikTokCLI):
    def __init__(self, parameter):
        super().__init__(parameter)
