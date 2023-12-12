import copy
from typing import List
import sys
import logging
from dataclasses import dataclass
from input_parser import DATParser
import time

OrderSchedule = List[bool]


def get_logger(name) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    return logger


logger = get_logger(__name__)

@dataclass
class Order:
    id: str
    profit: int
    length: int
    min_delivery: int
    max_delivery: int
    surface: int


@dataclass
class TimeSlotCapacity:
    id: str
    free_surface: int


@dataclass
class Solution:
    taken_orders: List[bool]
    profit: int
    schedule: List[OrderSchedule]
    occupation: List[TimeSlotCapacity]


@dataclass
class Input:
    n: int
    t: int
    profit: List[int]
    length: List[int]
    max_delivery: List[int]
    min_delivery: List[int]
    surface: List[int]
    surface_capacity: int


@dataclass
class Candidate:
    schedule: List[int]
    cost: int


@dataclass
class BaseSolver:

    input_data: Input
    config: DATParser

    def get_elapsed_time(self, start_time: float) -> float:
        return time.time() - start_time

    def get_orders(self):

        orders = []

        for i in range(self.input_data.n):
            order = Order(
                i,
                self.input_data.profit[i],
                self.input_data.length[i],
                self.input_data.min_delivery[i],
                self.input_data.max_delivery[i],
                self.input_data.surface[i]
            )
            orders.append(order)

        return orders

    def add_schedule(self, order: Order, schedule: OrderSchedule, solution: Solution) -> Solution:

        solution.profit += order.profit
        solution.taken_orders[order.id] = True
        solution.schedule[order.id] = schedule

        for i in range(self.input_data.t):
            if schedule[i]:
                solution.occupation[i].free_surface -= order.surface

        return solution

    def remove_order_schedule(self, order: Order, solution: Solution) -> Solution:

        schedule = solution.schedule[order.id]

        solution.taken_orders[order.id] = False
        solution.profit -= order.profit

        for i in range(self.input_data.t):
            if schedule[i]:
                solution.occupation[i].free_surface += order.surface

        solution.schedule[order.id] = [False] * self.input_data.t

        return solution

    def evaluate_schedules(self, order: Order, schedules: List[OrderSchedule], solution: Solution) -> List[Candidate]:

        candidates = []

        for schedule in schedules:

            potential_solution = copy.deepcopy(solution)

            potential_solution = self.add_schedule(order, schedule, potential_solution)

            occupied_surface = [self.input_data.surface_capacity - slot.free_surface for slot in potential_solution.occupation]

            # minimize the average time slot occupation
            cost = int(sum(occupied_surface) / len(occupied_surface))

            candidate = Candidate(schedule, cost)

            candidates.append(candidate)

        return candidates

    def get_feasible_schedules(self, order: Order, partial_solution: Solution) -> List[OrderSchedule]:

        slots = partial_solution.occupation

        # logger.info("Order index: %s', order reqs: %s, slots availability: %s", order.id, order, slots)
        schedule_length = len(partial_solution.schedule[0])

        feasible_schedules = []

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

                    feasible_schedules.append(order_schedule)

        return feasible_schedules

