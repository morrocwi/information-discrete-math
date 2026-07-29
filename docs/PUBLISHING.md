# Publishing to PyPI

The package metadata is publish-ready (`pyproject.toml`: name `information-discrete-math`, MIT license,
README as the long description, trove classifiers, project URLs). The build has been verified — a wheel
installs into a clean environment and `import idm` solves correctly. The **only** remaining step needs a
**PyPI API token**, which a human must run in a real terminal.

## Founder checklist (one-time)

1. **Name availability** — confirm `information-discrete-math` is free (or owned) on PyPI:
   <https://pypi.org/project/information-discrete-math/>. If taken, pick a name and update
   `pyproject.toml` `[project] name` + this doc.
2. **Token** — create a PyPI API token (Account → API tokens), scope it to the project once it exists
   (first upload can use an account-scoped token). Keep it out of the repo — pass it via
   `TWINE_USERNAME=__token__` + `TWINE_PASSWORD=pypi-…` env vars, or `~/.pypirc`.

## Build + upload (run in a terminal)

```bash
cd information-discrete-math
python -m pip install --upgrade build twine        # twine is not installed in the agent environment
rm -rf dist build *.egg-info
python -m build                                     # → dist/*.tar.gz + dist/*.whl
python -m twine check dist/*                        # metadata lint (should PASS)

# smoke-test the built wheel in a throwaway venv before uploading
python -m venv /tmp/idm-wheeltest && /tmp/idm-wheeltest/bin/pip install dist/*.whl
/tmp/idm-wheeltest/bin/python -c "import idm; print(idm.__version__, len(idm.kinds())); print(idm.factorize(360360).value)"

# TestPyPI first (recommended), then the real index:
python -m twine upload --repository testpypi dist/*   # verify the listing renders at test.pypi.org
python -m twine upload dist/*                         # the real upload (needs the token)
```

After a successful upload, `pip install information-discrete-math` works from a clean environment —
that closes Track B gap 1 (one-command install).

## Notes

- **Version**: upload the release build (bump to the release version first — see the release process /
  `CHANGELOG.md`; `__version__`, `pyproject.toml`, and `capabilities.json` are kept in lock-step by the
  `test_version_consistency` CI gate). PyPI refuses to overwrite an existing version, so a fixed re-upload
  needs a new version number.
- **What ships**: the wheel bundles `idm` (+ `idm._solve_domains`, `idm.kernel*`), `retained_spectral`,
  and the vendored `idm._vendor_tools`/`idm._vendor_provefull` (mapped from `tools/`/`provefull/` in
  `pyproject.toml`), so `import idm` works from an installed package, not just a source checkout.
- `dist/` and `build/` are git-ignored — never commit build artifacts.
