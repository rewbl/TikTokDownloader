from src.application.main_complete import TikTokCLI

__all__ = ["Monitor"]


class Monitor(TikTokCLI):
    def __init__(self, parameter):
        super().__init__(parameter)
