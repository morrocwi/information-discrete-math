# optimization / paths
from idm._solve_core import *  # noqa: F401,F403

for _pn in ("shortest_path", "critical_path", "widest_path", "minimax_path", "reachability", "path_count"):
    _make_path(_pn)
