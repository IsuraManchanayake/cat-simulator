import argparse


def _validate_basic(args):
    pass


def parse_args():
    parser = argparse.ArgumentParser(
        description='Cat simulator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '--state_file',
        type=str,
        help='Load simulation from state file.',
    )
    parser.add_argument(
        '--population',
        type=int,
        default=10,
        help='Starting cat population.',
    )
    parser.add_argument(
        '--n_steps',
        type=int,
        default=10,
        help='Number of time steps.',
    )
    parser.add_argument(
        '--t_width',
        type=int,
        default=10,
        help='Terrain width.',
    )
    parser.add_argument(
        '--t_height',
        type=int,
        default=10,
        help='Terrain width.',
    )
    parser.add_argument(
        '--t_elevation_file',
        type=str,
        help='Terrain elevation as a text file. If specified, t_height and t_width are ignored. If not '
             'specified, terrain is chosen flat. If invalid, the simulation exits.',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=0,
        help='Random seed.',
    )
    args = parser.parse_args()

    _validate_basic(args)
    return args
