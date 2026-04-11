"""Entry point: starts the game window and main loop."""

from game.game import Game


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
