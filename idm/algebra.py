"""idm.algebra — optimization as linear algebra over discrete semirings.

Shortest / critical / widest / minimax paths, reachability, and path counts — one generalized
Floyd–Warshall parameterized by a semiring whose laws are machine-checked in `formal/IDM_Tropical.v`.
(Re-export of the verified `tools/aggregate.py`.)
"""
from . import _bridge  # noqa: F401
from aggregate import (
    Semiring, MIN_PLUS, MAX_PLUS, BOTTLENECK, MINIMAX, REACH, COUNT,
    all_pairs, mat_mul, walk_count,
)

def shortest_path(W):   return all_pairs(W, MIN_PLUS)      # min-plus
def critical_path(W):   return all_pairs(W, MAX_PLUS)      # max-plus (longest / scheduling)
def widest_path(W):     return all_pairs(W, BOTTLENECK)    # max-min (bottleneck capacity)
def minimax_path(W):    return all_pairs(W, MINIMAX)       # min-max
def reachability(W):    return all_pairs(W, REACH)         # boolean transitive closure
def path_count(A):      return walk_count(A)               # sum-product walk/path counts

__all__ = ["Semiring", "MIN_PLUS", "MAX_PLUS", "BOTTLENECK", "MINIMAX", "REACH", "COUNT",
           "all_pairs", "mat_mul", "walk_count", "shortest_path", "critical_path", "widest_path",
           "minimax_path", "reachability", "path_count"]
