"""idm.server — a zero-dependency REST API for the finite-discrete solver.

Pure Python standard library (http.server) so it runs anywhere with no install — the same "run it
anywhere" ethos as the rest of the project. Endpoints:

    GET  /health          → {status, version, theorems, engine}
    GET  /                → this index (endpoint catalogue + example bodies)
    GET  /openapi.json    → a minimal OpenAPI 3 description
    POST /solve           → body: a structured problem {kind, ...}; returns the certified result

Start it:  python3 -m idm.server   (or)  idm-serve   (or)  python3 -c "import idm; idm.serve()"
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import __version__
from .solve import solve, kinds

EXAMPLES = {
    "constant":         {"kind": "constant", "name": "pi"},
    "geometric_series": {"kind": "geometric_series", "r": "1/3", "eps": "1e-12"},
    "exp":              {"kind": "exp", "x": 0.4, "eps": "1e-20"},
    "integral":         {"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": "1e-8"},
    "double_integral":  {"kind": "double_integral", "f": "exp(-(x+y))", "ax": 0, "bx": 1, "ay": 0, "by": 1},
    "derivative":       {"kind": "derivative", "f": "exp(x)", "x": 1},
    "limit":            {"kind": "limit", "seq": "(1 + 1/n)**n"},
    "ode":              {"kind": "ode", "f": "y", "x0": 0, "y0": 1, "xT": 1},
    "zeta":             {"kind": "zeta", "s": -1},
    "regularized_sum":  {"kind": "regularized_sum", "power": 1},
    "root_find":        {"kind": "root_find", "f": "x*x - 2", "a": 0, "b": 2},
    "minimize":         {"kind": "minimize", "f": "(x-3)**2 + 1", "a": 0, "b": 6},
    "factorize":        {"kind": "factorize", "n": 360360},
    "is_prime":         {"kind": "is_prime", "n": 1000003},
    "fibonacci":        {"kind": "fibonacci", "n": 100},
    "partition":        {"kind": "partition", "n": 100},
    "crt":              {"kind": "crt", "residues": [2, 3, 2], "moduli": [3, 5, 7]},
    "matrix_determinant": {"kind": "matrix_determinant", "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 10]]},
    "solve_linear":     {"kind": "solve_linear", "A": [[2, 1], [1, 3]], "b": [3, 5]},
    "eigenvalues":      {"kind": "eigenvalues", "matrix": [[2, 0, 0], [0, 3, 0], [0, 0, 5]]},
    "rational_roots":   {"kind": "rational_roots", "coeffs": [-6, 11, -6, 1]},
    "shortest_path":    {"kind": "shortest_path", "matrix": [[0, 3, None], [3, 0, 1], [None, 1, 0]], "source": 0, "target": 2},
    "readouts":         {"kind": "readouts", "data": [3, -1, 4, 1, -5, 9, 2, -6]},
}
INDEX = {
    "name": "Information Discrete Mathematics — Solver API",
    "version": __version__,
    "principle": "Every answer is a finite discrete rational readout. No continuum call produces a value.",
    "endpoints": {
        "GET /health": "liveness + version",
        "GET /openapi.json": "OpenAPI 3 description",
        "POST /solve": "solve a structured problem; body examples below",
    },
    "problem_kinds": kinds(),
    "examples": EXAMPLES,
}
OPENAPI = {
    "openapi": "3.0.3",
    "info": {"title": "Information Discrete Mathematics Solver", "version": __version__,
             "description": "Finite-discrete, tier-honest solver. Returns value, proven bound, status, tier."},
    "paths": {
        "/solve": {"post": {"summary": "Solve a structured finite-discrete problem",
                            "requestBody": {"required": True,
                                            "content": {"application/json": {"examples": {k: {"value": v} for k, v in EXAMPLES.items()}}}},
                            "responses": {"200": {"description": "certified result"}}}},
        "/health": {"get": {"summary": "Liveness", "responses": {"200": {"description": "ok"}}}},
    },
}


class _Handler(BaseHTTPRequestHandler):
    server_version = "idm/" + __version__

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/"):
            self._send(200, INDEX)
        elif self.path == "/health":
            self._send(200, {"status": "ok", "version": __version__, "theorems_axiom_free": 55,
                             "engine": "finite-discrete (mpmath rational core)"})
        elif self.path == "/openapi.json":
            self._send(200, OPENAPI)
        elif self.path.rstrip("/") == "/kinds":
            self._send(200, {"count": len(kinds()), "kinds": kinds()})
        else:
            self._send(404, {"status": "HOLD", "reason": f"no route {self.path}"})

    def do_POST(self):
        if self.path.rstrip("/") != "/solve":
            self._send(404, {"status": "HOLD", "reason": f"no route {self.path}"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            problem = json.loads(self.rfile.read(n) or b"{}")
        except Exception as ex:
            self._send(400, {"status": "HOLD", "reason": f"invalid JSON body: {ex}"})
            return
        try:
            self._send(200, solve(problem))
        except Exception as ex:                       # a solver failure is a HOLD, never a crash
            self._send(200, {"status": "HOLD", "kind": problem.get("kind"), "reason": f"{type(ex).__name__}: {ex}"})

    def log_message(self, *a):                        # quiet by default
        pass


def run(host="127.0.0.1", port=8737):
    srv = ThreadingHTTPServer((host, port), _Handler)
    print(f"idm solver API on http://{host}:{port}  (POST /solve · GET /health · GET /openapi.json)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Information Discrete Mathematics — solver API")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8737)
    a = ap.parse_args()
    run(a.host, a.port)
