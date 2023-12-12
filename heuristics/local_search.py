import copy
from typing import Optional
from utils import Solution
from utils import BaseSolver
from utils import Order
from utils import get_logger
import time

logger = get_logger(__name__)


class LocalSearch(BaseSolver):

    name: str = 'Local Search'

    def explore_neighborhood(self, solution: Solution, orders: Order) -> Optional[Solution]:

        best_profit = solution.profit
        best_neighbor_solution = None

        rejected_orders_idx = [idx for idx, value in enumerate(solution.taken_orders) if not value]
        accepted_orders_idx = [idx for idx, value in enumerate(solution.taken_orders) if value]

        for idx_r in rejected_orders_idx:

            order_r = orders[idx_r]

            logger.debug("\t [%s] Attempting to schedule rejected order %s", self.name, order_r.id)

            for idx_a in accepted_orders_idx:

                order_a = orders[idx_a]

                new_solution = copy.deepcopy(solution)

                new_solution = self.remove_order_schedule(order_a, new_solution)

                logger.debug("\t * Removed schedule for order %s", order_a.id)

                neighbors_r = self.get_feasible_schedules(order_r, new_solution)

                if not neighbors_r:
                    logger.debug("\t\t Unable to schedule rejected order")

                else:

                    for i, neighbor_r in enumerate(neighbors_r):

                        new_solution_r = self.add_schedule(order_r, neighbor_r, new_solution)
                        logger.debug("\t\t Scheduled rejected order %s (candidate %s)", order_r.id, i+1)

                        if new_solution_r.profit > best_profit:
                            logger.debug("\t\t\t [%s] Improved solution from %s to %s", self.name, best_profit, new_solution_r.profit)
                            best_neighbor_solution = new_solution_r
                            best_profit = best_neighbor_solution.profit

                        else:
                            logger.debug("\t\t\t Did not improve the solution")

                        neighbors_a = self.get_feasible_schedules(order_a, new_solution_r)

                        if not neighbors_a:
                            logger.debug("\t\t\t Unable to reschedule removed order")

                        else:

                            for neighbor_a in neighbors_a:

                                new_solution_a = copy.deepcopy(new_solution_r)

                                new_solution_a = self.add_schedule(order_a, neighbor_a, new_solution_a)

                                logger.debug("\t\t\t Reassigned order %s", order_a.id)

                                if new_solution_a.profit > best_profit:
                                    logger.debug("\t [%s] Improved solution from %s to %s", self.name, best_profit, new_solution_a.profit)
                                    best_neighbor_solution = new_solution_a
                                    best_profit = best_neighbor_solution.profit

        return best_neighbor_solution

    def solve(self, initial_solution: Solution, start_time: float) -> Solution:

        best_solution = initial_solution
        highest_profit = initial_solution.profit

        orders = self.get_orders()

        while (False in best_solution.taken_orders) \
                and self.get_elapsed_time(start_time) < self.config.maxExecTime:

            neighbor = self.explore_neighborhood(best_solution, orders)

            if neighbor is None:
                logger.debug("[%s] No neighbors found", self.name)
                break;

            elif neighbor.profit < highest_profit:
                logger.debug("[%s] Neighbor found but the solution is not improved", self.name)
                break;

            highest_profit = neighbor.profit
            best_solution = neighbor

            logger.info("[%s] Objective: %s. Elapsed time: %s", self.name, best_solution.profit,
                        self.get_elapsed_time(start_time))

        return best_solution


