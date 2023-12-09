import sys
import logging
from utils import Solution

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


class LocalSearch:

    def solve(self, initial_solution: Solution) -> Solution:
        pass

