import random

from args import parse_args
from state import State


def main():
    args = parse_args()
    state = State(args)
    state.start()

    print(state.terrain)


if __name__ == '__main__':
    main()
