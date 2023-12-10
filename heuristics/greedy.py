from typing import List
from utils import Solution
from utils import get_logger
from utils import TimeSlotCapacity
from utils import OrderSchedule
from utils import BaseSolver

logger = get_logger(__name__)


class Greedy(BaseSolver):

    def get_best_candidate(self, candidates: List[OrderSchedule]) -> OrderSchedule:

        start_slot_idx = [schedule.index(True) for schedule in candidates]
        best_idx = start_slot_idx.index(min(start_slot_idx))

        return candidates[best_idx]

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

            candidates = self.get_candidates(order, partial_solution)

            logger.debug("Order index: %s, candidates: %s", order.id, candidates)

            if candidates:
                schedule = self.get_best_candidate(candidates)

                logger.debug("Order index: %s, schedule: %s", order.id, schedule)

                partial_solution = self.add_order_schedule(order, schedule, partial_solution)

        solution = partial_solution

        return solution
