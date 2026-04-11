"""程序入口：启动游戏窗口与主循环。"""

from game.game import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
