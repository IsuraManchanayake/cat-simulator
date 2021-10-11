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
        '--hour_of_day',
        type=int,
        default=0,
        help='Starting hour of simulation.',
    )
    parser.add_argument(
        '--neighborhood',
        type=str,
        default='moore',
        choices=('moore', 'von-neumann'),
        help='Neighborhood algorithm.',
    )
    parser.add_argument(
        '--neighborhood_radius',
        type=int,
        default=3,
        help='Neighborhood radius.',
    )
    parser.add_argument(
        '--continuous_food',
        action='store_true',
        help='Flag to set continuous food suppy at food locations. If not set, food will be set periodically at the '
             '12th hour of the day.',
    )
    parser.add_argument(
        '--t_elevations_file',
        type=str,
        help='Terrain elevations as a text file. If specified, t_height and t_width are ignored. If not '
             'specified, elevations are set to 0. If invalid, the simulation exits.',
    )
    parser.add_argument(
        '--t_cell_types_file',
        type=str,
        help='Terrain cell types as a text file. If specified, t_height and t_width are ignored. If not '
             'specified, cell types are chosen random. If invalid, the simulation exits.',
    )
    parser.add_argument(
        '--log_file_path',
        type=str,
        help='All logs go into this file.',
        default='simulation.log'
    )
    parser.add_argument(
        '--results_file_path',
        type=str,
        help='Simulation results as json file.',
        default='simulation-results.json',
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
