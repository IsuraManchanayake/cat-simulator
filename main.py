from args import parse_args
from catsim.simulation import Simulation
from catsim.logging import Logger, LogMethod


def main():
    args = parse_args()

    # Logger.setup(LogMethod.file, args.log_file_path)
    Logger.setup(LogMethod.none)

    simulation = Simulation(args)
    # simulation.render_enabled = False
    simulation.start()


if __name__ == '__main__':
    main()
