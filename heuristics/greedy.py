from typing import List
from utils import Solution
from utils import get_logger
from utils import TimeSlotCapacity
from utils import Candidate
from utils import BaseSolver

logger = get_logger(__name__)


class Greedy(BaseSolver):

    def get_best_candidate(self, candidates: List[Candidate]) -> Candidate:

        candidates_sorted = sorted(candidates, key=lambda x: x.cost)
        return candidates_sorted[0]

    def solve(self) -> Solution:

        orders = self.get_orders()

        partial_solution = Solution(
            taken_orders=[False]*self.input_data.n,
            profit=0,
            schedule=[[False]*self.input_data.t for i in range(self.input_data.n)],
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

            logger.debug("Order index: %s, candidates: %s", order.id, candidates)

            if candidates:

                candidate = self.get_best_candidate(candidates)

                logger.debug("Order index: %s, schedule: %s", order.id, candidate.schedule)

                partial_solution = self.add_schedule(order, candidate.schedule, partial_solution)

        solution = partial_solution

        return solution
