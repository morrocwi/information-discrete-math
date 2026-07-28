# Makefile — navigation shortcuts for Information Discrete Mathematics.
# Every target just wraps a command already documented in README.md / API.md; none of these do
# anything you cannot also run by hand. `verify-all` is meant for once-before-commit use, not
# per-edit iteration (see AGENTS.md on repeated full-arc audits).

.PHONY: install discover test prove formal benchmark verify-all

install:
	pip install -e ".[spectral-bench]"

discover:
	python3 -c "import idm; print(idm.kinds())"

test:
	pytest -q

prove:
	python3 prove_it_full.py

formal:
	bash formal/verify.sh

benchmark:
	python3 -m retained_spectral.competition.run

verify-all: test prove formal
