from time import sleep

from src.Infrastructure.module import ColorfulConsole

__all__ = ["choose"]


def choose(
        title: str,
        options: tuple | list,
        console: ColorfulConsole,
        separate=None,
        test_return=None) -> str:

    if test_return:
        sleep(1)
        return test_return
    screen = f"{title}:\n"
    row = 0
    for i, j in enumerate(options, start=1):
        screen += f"{i: >2d}. {j}\n"
        if separate and row in separate:
            screen += f"{'=' * 25}\n"
        row += 1
    return console.input(screen)

