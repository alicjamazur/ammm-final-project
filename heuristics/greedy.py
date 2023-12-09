import sys
import logging
from typing import List
from utils import Solution
from utils import Input
from utils import Order
from utils import TimeSlotCapacity
from utils import OrderSchedule


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class Greedy:

    def create_orders_and_slots(self, input_data):

        orders = []
        slots = []

        for i in range(input_data.n):
            order = Order(
                i,
                input_data.profit[i],
                input_data.length[i],
                input_data.min_delivery[i],
                input_data.max_delivery[i],
                input_data.surface[i]
            )
            orders.append(order)

        for j in range(input_data.t):
            slot = TimeSlotCapacity(j, input_data.surface_capacity)
            slots.append(slot)

        return orders, slots

    def get_candidates(self, order: Order, partial_solution: Solution) -> List[OrderSchedule]:

        slots = partial_solution.occupation

        # logger.info("Order index: %s', order reqs: %s, slots availability: %s", order.id, order, slots)
        schedule_length = len(partial_solution.schedule[0])

        candidates = []

        for delivery_id in range(order.min_delivery, order.max_delivery + 1):

            feasible = True

            for i in range(order.length):

                # adjustment due to python indexing
                delivery_idx = delivery_id - 1

                if slots[delivery_idx - i].free_surface < order.surface:
                    feasible = False
                    break

            if feasible:
                start_idx = delivery_idx - order.length + 1
                end_idx = delivery_idx

                if start_idx >= 0:
                    order_schedule = [True if start_idx <= i <= end_idx else False for i in range(schedule_length)]

                    candidates.append(order_schedule)

        return candidates

    def get_best_candidate(self, candidates: List[OrderSchedule]) -> OrderSchedule:

        start_slot_idx = [schedule.index(True) for schedule in candidates]
        best_idx = start_slot_idx.index(min(start_slot_idx))

        return candidates[best_idx]

    def solve(self, input_data: Input) -> Solution:

        orders, slots = self.create_orders_and_slots(input_data)

        partial_solution = Solution(
            taken_orders=[False]*input_data.n,
            profit=0,
            schedule=[[False]*input_data.t for i in range(input_data.n)],
            occupation=slots
        )

        sorted_orders = sorted(
                orders,
                key=lambda x: x.profit,
                reverse=True
        )

        for order in sorted_orders:

            candidates = self.get_candidates(order, partial_solution)

            # logger.info("Order index: %s, candidates: %s", order.id, candidates)

            if candidates:
                selection = self.get_best_candidate(candidates)

                # logger.info("Order index: %s, schedule: %s", order.id, selection)

                partial_solution.profit += order.profit
                partial_solution.taken_orders[order.id] = True
                partial_solution.schedule[order.id] = selection

                for i in range(input_data.t):
                    if selection[i]:
                        partial_solution.occupation[i].free_surface -= order.surface

        solution = partial_solution

        logger.info("Solution: %s", solution)

        return solution
