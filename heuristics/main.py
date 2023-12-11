import sys
import time
import logging
from argparse import ArgumentParser
from pathlib import Path

from input_parser import DATParser
from local_search import LocalSearch
from greedy import Greedy
from grasp import GRASP
from utils import Input

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


if __name__ == '__main__':
    parser = ArgumentParser(description='AMMM Final Project')
    parser.add_argument('-c', '--configFile', nargs='?', type=Path,
                        default=Path(__file__).parent / 'config/config.dat', help='specifies the config file')
    args = parser.parse_args()

    config = DATParser.parse(args.configFile)
    parsed_data = DATParser.parse(config.inputDataFile)

    data = Input(
        n=parsed_data.n,
        t=parsed_data.t,
        profit=list(parsed_data.profit),
        length=list(parsed_data.length),
        min_delivery=list(parsed_data.min_deliver),
        max_delivery=list(parsed_data.max_deliver),
        surface=list(parsed_data.surface),
        surface_capacity=parsed_data.surface_capacity,
    )

    start_time = time.time()

    if config.solver == 'Greedy':

        greedy = Greedy(data, config)
        solution = greedy.solve()

    elif config.solver == 'GRASP':

        grasp = GRASP(data, config)
        solution = grasp.solve()

    logger.info("[%s] Elapsed time: %s seconds", config.solver, time.time() - start_time)
    logger.info('[%s] Optimal profit: %s', config.solver, solution.profit)

    rejected_orders = False in solution.taken_orders

    if rejected_orders and config.localSearch:

        logger.info("[Local Search] Attempting to improve the solution")

        local_search = LocalSearch(data, config)

        solution = local_search.solve(
            initial_solution=solution,
        )

        logger.info("[Local Search] Elapsed time: %s seconds", time.time() - start_time)

        logger.info('[Local Search] Optimal profit: %s', solution.profit)
