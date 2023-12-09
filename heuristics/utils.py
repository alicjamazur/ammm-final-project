from typing import List
from dataclasses import dataclass

OrderSchedule = List[bool]


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

