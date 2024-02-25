from atexit import register
from contextlib import suppress
from pathlib import Path
from threading import Event
from threading import Thread

from src.Infrastructure.custom import COOKIE_UPDATE_INTERVAL
from src.Infrastructure.custom import (
    PROJECT_ROOT,
    VERSION_MAJOR,
    VERSION_MINOR,
    VERSION_BETA,
)
from src.Infrastructure.custom import TEXT_REPLACEMENT
from src.Infrastructure.manager import DownloadRecorder
from src.Infrastructure.module import ColorfulConsole
from src.Infrastructure.module import Cookie
from src.Infrastructure.record import LoggerManager
from src.Infrastructure.tools import FileSwitch
from src.Infrastructure.tools import choose
from src.config import RuntimeParameters
from src.config import Settings
from .TikTokCLI import TikTokCLI

__all__ = ["TikTokDownloader"]

from ..config.AppConfig import XBogusInstance


def start_cookie_task(function):
    def inner(self, *args, **kwargs):
        if not self.cookie_task.is_alive():
            self.cookie_task.start()

        return function(self, *args, **kwargs)

    return inner


class AppBase:
    NAME = f"TikTokDownloader v{VERSION_MAJOR}.{VERSION_MINOR}{'Beta' if VERSION_BETA else ''}"
    WIDTH = 50
    LINE = ">" * WIDTH

    def __init__(self):
        self.console = ColorfulConsole()
        self.blacklist = None
        self.runtime_parameters = None

        self.event = Event()
        self.cookie = None
        self.settings = None
        self.cookie_task = None

    def periodic_update_cookie(self):
        while not self.event.is_set():
            self.runtime_parameters.update_cookie()
            self.event.wait(COOKIE_UPDATE_INTERVAL)

    def close(self):
        self.event.set()
        self.blacklist.close()

    def check_settings(self):
        self.runtime_parameters = RuntimeParameters(
            self.settings,
            self.cookie,
            main_path=PROJECT_ROOT,
            logger=LoggerManager,
            xb=XBogusInstance,
            console=self.console,
            **self.settings.read(),
            blacklist=self.blacklist,
        )
        self.runtime_parameters.cleaner.set_rule(TEXT_REPLACEMENT, True)

    def write_cookie(self):
        self.cookie.run()
        self.check_settings()
        self.runtime_parameters.update_cookie()

    def check_config(self):
        folder = ("./src", "./src/config", "./cache", "./cache/temp")
        for i in folder:
            PROJECT_ROOT.joinpath(i).mkdir(exist_ok=True)
        self.blacklist = DownloadRecorder(
            False,
            PROJECT_ROOT.joinpath("./cache"),
            self.console)

    def change_config(self, file: Path):
        FileSwitch.deal_config(file)
        self.console.print("修改设置成功！")
        if self.blacklist:
            self.blacklist.close()
        self.check_config()
        self.check_settings()


class TikTokDownloader(AppBase):

    def __init__(self):
        super().__init__()
        self.settings = Settings(PROJECT_ROOT, self.console)
        self.cookie = Cookie(self.settings, self.console)
        self.running = True
        self.cookie_task = Thread(target=self.periodic_update_cookie)
        self.__function = None

    # region CLI menu
    def __update_menu(self):
        self.__function = (
            ("复制粘贴写入 Cookie(推荐)", self.write_cookie),
            ("扫码登录写入 Cookie(弃用)", self.write_cookie),
            ("终端交互模式", self.complete),
        )

    def main_menu(self, default_mode="0"):
        """选择运行模式"""
        while self.running:
            self.__update_menu()
            if default_mode not in {"3"}:
                default_mode = choose(
                    "请选择 TikTokDownloader 运行模式",
                    [i for i, _ in self.__function],
                    self.console,
                    separate=(
                        1,
                        6),
                    test_return='3')
            self.compatible(default_mode)
            default_mode = "0"

    # endregion

    @start_cookie_task
    def complete(self):
        """终端交互模式"""
        example = TikTokCLI(self.runtime_parameters)
        register(self.blacklist.close)
        try:
            example.run()
            self.running = example.running
        except KeyboardInterrupt:
            self.running = False

    def compatible(self, mode: str):
        with suppress(ValueError):
            if mode in {"Q", "q", ""}:
                self.running = False
            elif (n := int(mode) - 1) in range(len(self.__function)):
                self.__function[n][1]()

    def run(self):
        self.check_config()
        self.check_settings()
        self.main_menu(self.runtime_parameters.default_mode)
        self.close()
