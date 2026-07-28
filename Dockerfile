# idm-core — the finite-discrete solver + REST server (idm/server.py), no numeric extras.
# Minimal, standard image: pip-installs the wheel exactly as published to PyPI-style consumers.
FROM python:3.11-slim

WORKDIR /app

# Copy only what the build backend (setuptools) declares as packages/package-data, plus the
# files pyproject.toml/README.md reference directly (long_description, license), so the
# Docker build context matches a normal `pip install .` from a checkout.
COPY pyproject.toml README.md ./
COPY idm ./idm
COPY tools ./tools
COPY provefull ./provefull
COPY retained_spectral ./retained_spectral

RUN pip install --no-cache-dir .

EXPOSE 8737

# NOTE: the `idm-serve` console script (idm.server:run) binds 127.0.0.1 by default, which is
# unreachable from outside the container even with `-p`. `python -m idm.server` goes through the
# module's __main__ argparse block, which does accept --host, so we can bind 0.0.0.0 for container use.
CMD ["python", "-m", "idm.server", "--host", "0.0.0.0"]
