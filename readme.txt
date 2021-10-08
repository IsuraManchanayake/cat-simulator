Setting up
----------

If you wish to use a virtual environment,

$ python3 -m venv env

Windows
$ env\Scripts\activate

Linux
$ env/bin/activate


Installing packages
-------------------

$ pip install -r requirements.txt


Usage
-----

main.py [-h] [--state_file STATE_FILE] [--population POPULATION]
               [--n_steps N_STEPS] [--t_width T_WIDTH] [--t_height T_HEIGHT]
               [--hour_of_day HOUR_OF_DAY]
               [--neighborhood {moore,von-neumann}]
               [--neighborhood_radius NEIGHBORHOOD_RADIUS] [--continuous_food]
               [--t_elevations_file T_ELEVATIONS_FILE]
               [--t_cell_types_file T_CELL_TYPES_FILE] [--seed SEED]

Cat simulator

optional arguments:
  -h, --help            show this help message and exit
  --state_file STATE_FILE
                        Load simulation from state file. (default: None)
  --population POPULATION
                        Starting cat population. (default: 10)
  --n_steps N_STEPS     Number of time steps. (default: 10)
  --t_width T_WIDTH     Terrain width. (default: 10)
  --t_height T_HEIGHT   Terrain width. (default: 10)
  --hour_of_day HOUR_OF_DAY
                        Starting hour of simulation. (default: 0)
  --neighborhood {moore,von-neumann}
                        Neighborhood algorithm. (default: moore)
  --neighborhood_radius NEIGHBORHOOD_RADIUS
                        Neighborhood radius. (default: 3)
  --continuous_food     Flag to set continuous food suppy at food locations.
                        If not set, food will be set periodically at the 12th
                        hour of the day. (default: False)
  --t_elevations_file T_ELEVATIONS_FILE
                        Terrain elevations as a text file. If specified,
                        t_height and t_width are ignored. If not specified,
                        elevations are set to 0. If invalid, the simulation
                        exits. (default: None)
  --t_cell_types_file T_CELL_TYPES_FILE
                        Terrain cell types as a text file. If specified,
                        t_height and t_width are ignored. If not specified,
                        cell types are chosen random. If invalid, the
                        simulation exits. (default: None)
  --seed SEED           Random seed. (default: 0)


Example
-------

Example 1

$ python main.py --t_elevations_file elevation.txt --t_cell_types_file cell_types.txt --t_height 10 --t_width 10 --neighborhood von-neumann --neighborhood_radius 3 --population 10 --n_steps 10 --seed 0

Example 2

$ python main.py --t_height 30 --t_width 30 --neighborhood von-neumann --neighborhood_radius 3 --population 20 --n_steps 50 --seed 0


Log files
---------

The log file path is simulation.log