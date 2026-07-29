"""idm.server — a zero-dependency REST API for the finite-discrete solver, with OpenAPI + Swagger UI.

Pure Python standard library (http.server) so it runs anywhere with no install — the same "run it
anywhere" ethos as the rest of the project — yet it exposes the same world-class surface as a FastAPI
app: a full OpenAPI 3 document and an interactive Swagger UI, without taking on a web-framework
dependency. Endpoints:

    GET  /health          → {status, version, theorems, engine}
    GET  /                → this index (endpoint catalogue + example bodies)
    GET  /docs            → interactive Swagger UI (try any endpoint in the browser)
    GET  /openapi.json    → the full OpenAPI 3 description (schemas for every endpoint)
    GET  /kinds           → the catalogue of the 266 problem kinds
    POST /solve           → body: a structured problem {kind, ...} OR {text: "..."}; certified result
    POST /parse           → body: {text: "..."}; the world-language → structured translation (or HOLD)

Start it:  python3 -m idm.server   (or)  idm-serve   (or)  python3 -c "import idm; idm.serve()"
Then open  http://127.0.0.1:8737/docs  for the Swagger UI.
"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from . import __version__
from .solve import solve, kinds
from .parse import parse, parse_and_solve

EXAMPLES = {
    "constant":         {"kind": "constant", "name": "pi"},
    "geometric_series": {"kind": "geometric_series", "r": "1/3", "eps": "1e-12"},
    "exp":              {"kind": "exp", "x": 0.4, "eps": "1e-20"},
    "integral":         {"kind": "integral", "f": "1/exp(x*x)", "a": "-inf", "b": "inf"},
    "improper_integral": {"kind": "improper_integral", "f": "x**3/(exp(x)-1)", "a": "1e-14", "b": "inf", "eps": "1e-8"},
    "singular_integral": {"kind": "singular_integral", "f": "1/sqrt(x)", "a": "1e-30", "b": 1},
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
NL_EXAMPLES = {
    "integral":     {"text": "integrate x^2 from 0 to 1"},
    "prime":        {"text": "is 97 prime?"},
    "eigenvalues":  {"text": "eigenvalues of [[2,0],[0,3]]"},
    "limit":        {"text": "limit of sin(x)/x as x -> 0"},
    "factorize":    {"text": "prime factorization of 360360"},
}
INDEX = {
    "name": "Information Discrete Mathematics — Solver API",
    "version": __version__,
    "principle": "Every answer is a finite discrete rational readout. No continuum call produces a value.",
    "docs": "GET /docs  (interactive Swagger UI)",
    "endpoints": {
        "GET /health": "liveness + version",
        "GET /docs": "interactive Swagger UI",
        "GET /openapi.json": "full OpenAPI 3 description",
        "GET /kinds": "catalogue of problem kinds",
        "POST /solve": "solve a structured problem {kind,…} or {text:…}; examples below",
        "POST /parse": "translate a world-language request {text:…} into a structured kind (or HOLD)",
    },
    "problem_kinds": kinds(),
    "examples": EXAMPLES,
    "natural_language_examples": NL_EXAMPLES,
}

_RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "description": "the problem kind that was solved"},
        "status": {"type": "string", "enum": ["ok", "CERTIFIED", "HOLD"],
                   "description": "CERTIFIED = proven bound; ok = finite readout; HOLD = honest refusal"},
        "value": {"description": "the answer; exact ℚ as {exact,float}, reals as {digits,float}, complex as {re,im}"},
        "tier": {"type": "string", "enum": ["Th_coqc", "finite_diagnostic"],
                 "description": "Th_coqc = machine-checked axiom-free; finite_diagnostic = numeric to tolerance"},
        "method": {"type": "string"}, "error_bound": {"description": "proven bound where one exists"},
        "reason": {"type": "string", "description": "why a HOLD was returned"},
    },
    "required": ["status"],
}
OPENAPI = {
    "openapi": "3.0.3",
    "info": {
        "title": "Information Discrete Mathematics — Solver API",
        "version": __version__,
        "description": ("A finite-discrete, tier-honest mathematics solver. Every answer is a finite discrete "
                        "rational readout — no continuum library call ever produces a value. Each result carries "
                        "a `status` (CERTIFIED / ok / HOLD), a `tier` (Th_coqc machine-checked / finite_diagnostic), "
                        "the method used, and a proven error bound where one exists. An unknown or unprovable "
                        "request returns HOLD, never a wrong answer. Developed by Yaoharee Lahtee."),
        "contact": {"name": "Yaoharee Lahtee", "url": "https://github.com/morrocwi/information-discrete-math"},
        "license": {"name": "MIT"},
    },
    "externalDocs": {"description": "Full treatise & source", "url": "https://github.com/morrocwi/information-discrete-math"},
    "servers": [{"url": "/"}],
    "tags": [
        {"name": "solve", "description": "run the solver"},
        {"name": "translate", "description": "world-language → structured problem"},
        {"name": "meta", "description": "health, catalogue, spec"},
    ],
    "paths": {
        "/solve": {"post": {
            "tags": ["solve"], "operationId": "solve",
            "summary": "Solve a structured finite-discrete problem",
            "description": "Body is a structured problem `{kind, …}`, or `{text: '…'}` to translate first then solve.",
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": {"type": "object", "properties": {"kind": {"type": "string", "enum": kinds()},
                                                            "text": {"type": "string", "description": "world-language request (translated then solved)"}},
                           "additionalProperties": True},
                "examples": {**{k: {"summary": k, "value": v} for k, v in EXAMPLES.items()},
                             **{"NL: " + k: {"summary": "natural language — " + k, "value": v} for k, v in NL_EXAMPLES.items()}}}}},
            "responses": {"200": {"description": "certified / ok / HOLD result",
                                  "content": {"application/json": {"schema": _RESULT_SCHEMA}}}}}},
        "/parse": {"post": {
            "tags": ["translate"], "operationId": "parse",
            "summary": "Translate a world-language request into a structured kind",
            "description": "Deterministic rule-based translation. Returns the structured `{kind,…}` (echoing the "
                           "source so it is checkable) or HOLD with candidate kinds — it never mis-routes.",
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]},
                "examples": {k: {"value": v} for k, v in NL_EXAMPLES.items()}}}},
            "responses": {"200": {"description": "structured problem or HOLD"}}}},
        "/kinds": {"get": {"tags": ["meta"], "operationId": "listKinds", "summary": "List all problem kinds",
                           "responses": {"200": {"description": "count + kinds array"}}}},
        "/health": {"get": {"tags": ["meta"], "operationId": "health", "summary": "Liveness + version",
                            "responses": {"200": {"description": "ok"}}}},
        "/openapi.json": {"get": {"tags": ["meta"], "operationId": "openapi", "summary": "This OpenAPI document",
                                  "responses": {"200": {"description": "OpenAPI 3 spec"}}}},
    },
    "components": {"schemas": {"Result": _RESULT_SCHEMA}},
}

_SWAGGER_HTML = """<!doctype html><html><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Information Discrete Mathematics — Solver API</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"/>
<style>body{margin:0}.topbar{display:none}</style></head><body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>window.onload=function(){window.ui=SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui',
deepLinking:true,tryItOutEnabled:true,presets:[SwaggerUIBundle.presets.apis]});};</script>
</body></html>"""


class _Handler(BaseHTTPRequestHandler):
    server_version = "idm/" + __version__

    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False, indent=2, default=str).encode("utf-8")
        self._raw(code, body, "application/json; charset=utf-8")

    def _raw(self, code, body, ctype):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        p = self.path.rstrip("/")
        if p in ("", "/"):
            self._send(200, INDEX)
        elif p == "/docs":
            self._raw(200, _SWAGGER_HTML.encode("utf-8"), "text/html; charset=utf-8")
        elif p == "/health" or self.path == "/health":
            self._send(200, {"status": "ok", "version": __version__, "theorems_axiom_free": 55,
                             "kinds": len(kinds()), "engine": "finite-discrete (mpmath rational core)"})
        elif self.path == "/openapi.json":
            self._send(200, OPENAPI)
        elif p == "/kinds":
            self._send(200, {"count": len(kinds()), "kinds": kinds()})
        else:
            self._send(404, {"status": "HOLD", "reason": f"no route {self.path}"})

    def do_POST(self):
        route = self.path.rstrip("/")
        if route not in ("/solve", "/parse"):
            self._send(404, {"status": "HOLD", "reason": f"no route {self.path}"})
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
        except Exception as ex:
            self._send(400, {"status": "HOLD", "reason": f"invalid JSON body: {ex}"})
            return
        try:
            if route == "/parse":
                self._send(200, parse(body.get("text", "")))
            elif "text" in body and "kind" not in body:      # /solve with a world-language request
                self._send(200, parse_and_solve(body["text"]))
            else:
                self._send(200, solve(body))
        except Exception as ex:                       # a solver failure is a HOLD, never a crash
            self._send(200, {"status": "HOLD", "kind": body.get("kind"), "reason": f"{type(ex).__name__}: {ex}"})

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
