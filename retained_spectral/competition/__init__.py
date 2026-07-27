"""Reproducible competition harness for the Retained Spectral solver.

Two independent measurements live here:

* :mod:`retained_spectral.competition.scipy_pipeline` — an *independent*
  end-to-end SciPy pipeline that receives the same raw input as the native
  solver and owns its own well search, meshes, window expansion, and verdict.
* :mod:`retained_spectral.competition.executor_audit` — a same-operator
  executor comparison: native, SciPy, and JAX all solve one identical finite
  operator so only the solve kernel differs.

:mod:`retained_spectral.competition.run` orchestrates both and writes a JSON
record measured on the host machine; :mod:`retained_spectral.competition.chart`
renders the bar chart from that record.
"""
