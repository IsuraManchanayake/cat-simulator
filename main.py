import matplotlib.pyplot as plt

from args import parse_args
from catsim.simulation import Simulation
from catsim.logging import Logger, LogMethod


def main():
    args = parse_args()

    Logger.setup(LogMethod.file)

    simulation = Simulation(args)
    # simulation.render_enabled = False

    simulation.setup()
    while not simulation.finished():
        simulation.update()
    simulation.finalize()


if __name__ == '__main__':
    main()
