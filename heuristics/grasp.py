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

    def get_randomized_candidate(self, schedules: List[OrderSchedule], alpha: float) -> List[Candidate]:

        candidates = []

        for schedule in schedules:

            start_slot_idx = schedule.index(True)

            candidate = Candidate(
                schedule=schedule,
                q=start_slot_idx
            )

            candidates.append(candidate)

        sorted_candidates = sorted(candidates, key=lambda x: x.q)

        logger.debug("[%s] Candidates: %s", self.config.solver, sorted_candidates)

        q_min = sorted_candidates[0].q
        q_max = sorted_candidates[-1].q

        q_threshold = q_min + (q_max - q_min) * alpha

        max_index = 0
        for candidate in sorted_candidates:
            if candidate.q <= q_threshold:
                max_index += 1

        rcl = sorted_candidates[0:max_index]

        if not rcl:
            return None

        selection = random.choice(rcl)

        logger.debug("\t alpha: %s, q_min: %s, q_max: %s, q_threshold: %s, rcl: %s, selection: %s", alpha, q_min, q_max, q_threshold, rcl, selection.q)

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

            candidates = self.get_candidates(order, partial_solution)

            logger.debug("Order index: %s, candidates: %s", order.id, candidates)

            if candidates:

                schedule = self.get_randomized_candidate(candidates, alpha)

                logger.debug("Order index: %s, schedule: %s", order.id, schedule)

                partial_solution = self.add_order_schedule(order, schedule, partial_solution)

        solution = partial_solution

        logger.info("\t [Randomized Greedy] Best profit: %s", solution.profit)

        return solution

    def solve(self) -> Solution:

        iteration = 0
        start_time = time.time()
        rejected_orders = True

        while rejected_orders and \
                self.get_elapsed_time(start_time) < self.config.maxExecTime:

            iteration += 1
            logger.info("[GRASP] Iteration %s", iteration)

            alpha = 0 if iteration == 1 else self.config.alpha

            solution = self.solve_randomized_greedy(alpha)

            best_solution = solution

            rejected_orders = False in solution.taken_orders

            if rejected_orders and self.config.localSearch:

                logger.info("\t [Local Search] Attempting to improve the solution")

                local_search = LocalSearch(self.input_data, self.config)

                solution = local_search.solve(
                    initial_solution=solution,
                    start_time=start_time
                )

                rejected_orders = False in solution.taken_orders

                logger.debug("\t [Local Search] Elapsed time: %s seconds", time.time() - start_time)
                logger.info('\t [Local Search] Best profit: %s', solution.profit)

            if solution.profit > best_solution.profit:
                best_solution = solution

        return best_solution
