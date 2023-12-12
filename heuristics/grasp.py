from utils import BaseSolver
from utils import get_logger
from utils import Solution
from utils import TimeSlotCapacity
import time
from utils import Candidate
from utils import OrderSchedule
from local_search import LocalSearch
import random
from typing import List

logger = get_logger(__name__)


class GRASP(BaseSolver):

    name: str = 'GRASP'

    def get_randomized_candidate(self, candidates: List[Candidate], alpha: float) -> Candidate:

        sorted_candidates = sorted(candidates, key=lambda x: x.cost)

        logger.debug("[%s] Candidates: %s", self.name, sorted_candidates)

        q_min = sorted_candidates[0].cost
        q_max = sorted_candidates[-1].cost

        q_threshold = q_min + (q_max - q_min) * alpha

        logger.debug("q_min: %s, q_max: %s, q_threshold: %s", q_min, q_max, q_threshold)
        logger.debug("candidates with cost: %s", sorted_candidates)

        max_index = 0
        for candidate in sorted_candidates:
            if candidate.cost <= q_threshold:
                max_index += 1

        rcl = sorted_candidates[0:max_index]

        if not rcl:
            return None

        selection = random.choice(rcl)

        logger.debug("\t alpha: %s, rcl: %s/%s, selection: %s", alpha, len(rcl), len(sorted_candidates), selection.cost)

        return selection.schedule

    def solve_randomized_greedy(self, alpha: float) -> Solution:

        orders = self.get_orders()

        partial_solution = Solution(
            taken_orders=[False] * self.input_data.n,
            profit=0,
            schedule=[[False] * self.input_data.t for i in range(self.input_data.n)],
            occupation=[TimeSlotCapacity(i, self.input_data.surface_capacity) for i in range(self.input_data.t)]
        )

        sorted_orders = sorted(
            orders,
            key=lambda x: x.profit,
            reverse=True
        )

        for order in sorted_orders:

            schedules = self.get_feasible_schedules(order, partial_solution)

            candidates = self.evaluate_schedules(order, schedules, partial_solution)

            logger.debug("Order index: %s, candidates: %s", order.id, schedules)

            if candidates:

                schedule = self.get_randomized_candidate(candidates, alpha)

                logger.debug("Order index: %s, schedule: %s", order.id, schedule)

                partial_solution = self.add_schedule(order, schedule, partial_solution)

        solution = partial_solution

        rejected_orders = sum(not v for v in solution.taken_orders)

        logger.debug("\t [Randomized Greedy] Best profit: %s", solution.profit)
        logger.debug("\t [Randomized Greedy] Rejected orders: %s", rejected_orders)

        return solution

    def solve(self) -> Solution:

        iteration = 0
        start_time = time.time()
        rejected_orders = True

        best_solution = None

        while rejected_orders and \
                self.get_elapsed_time(start_time) < self.config.maxExecTime:

            iteration += 1
            logger.debug("[%s] Iteration %s", self.name, iteration)

            alpha = 0 if iteration == 1 else self.config.alpha

            base_solution = self.solve_randomized_greedy(alpha)

            if alpha == 0:
                logger.info("[Greedy] Objective: %s. Elapsed time: %s", base_solution.profit, self.get_elapsed_time(start_time))

            rejected_orders = False in base_solution.taken_orders

            if best_solution is None:
                best_solution = base_solution

            elif base_solution.profit > best_solution.profit:
                best_solution = base_solution

                logger.info("[%s] Objective: %s. Elapsed time: %s", self.name, best_solution.profit, self.get_elapsed_time(start_time))

            if rejected_orders and self.config.localSearch:

                local_search = LocalSearch(self.input_data, self.config)

                ls_solution = local_search.solve(
                    initial_solution=best_solution,
                    start_time=start_time
                )

                rejected_orders = False in ls_solution.taken_orders

                # logger.debug("\t [Local Search] Elapsed time: %s seconds", time.time() - start_time)
                # logger.info('\t [Local Search] Best profit: %s', ls_solution.profit)

                if ls_solution.profit > best_solution.profit:
                    best_solution = ls_solution

        logger.info("[%s] Best objective after %s iterations: %s", self.name, iteration, best_solution.profit)

        return best_solution
