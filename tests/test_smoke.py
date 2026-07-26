"""Smoke tests: prove_it reproduces the roots; the shipped tools self-check."""
import subprocess, sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _run(*a): return subprocess.run([sys.executable, *a], cwd=ROOT, capture_output=True, text=True)
def test_prove_it():   r=_run("prove_it.py"); assert r.returncode==0 and "10/10" in r.stdout, r.stdout[-400:]
def test_idm_tools():        assert _run("tools/idm_tools.py").returncode==0
def test_idm_discipline():   assert _run("tools/idm_discipline.py").returncode==0
def test_compliance():       assert _run("tools/framework_compliance.py").returncode==0
