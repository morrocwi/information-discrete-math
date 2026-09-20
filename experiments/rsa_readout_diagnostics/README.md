# IDM–RSA readout-conditioned factoring diagnostics

**Status: PROPOSAL / DIAGNOSTIC — NOT CANONICAL.** Nothing in this directory is
registered in Toledo (`github.com/morrocwi/toledo`); no equation here has an assigned
Toledo code. This is a disposable smoke-test log exploring whether an
Information-Discrete-Math ("readout-first") framing gives any measurable computational
advantage over classical integer-factoring practice (Dixon/QS-style relation
acquisition). Per Toledo's `TG-RFG-01` gate (Toledo lookup → Genesis compatibility →
reuse → derive only the missing piece → mark PROPOSAL), every object referenced here
(`PROP-IDM-RSA-01`..`08`) is a proposal only, with intended (not assigned) Toledo slots.

**Start here:**
- [`FINDINGS_SUMMARY.md`](./FINDINGS_SUMMARY.md) — condensed positive + negative
  findings, corrected overclaims, and documented (not-yet-executed) next steps.
- [`RESULTS_LOG.md`](./RESULTS_LOG.md) — full append-only entry-by-entry log (8
  entries), including two self-caught measurement corrections.

**Scripts** (each runnable standalone, `python3 <script>.py`, deterministic/seeded):
`calibrate_costs.py`, `smoke_dropsafe_vs_sieve_threshold.py`,
`smoke_rsa04_rrr_gate_vacuity.py`, `smoke_rsa05_cost_fold.py`,
`smoke_rsa08_gen2_staged.py`, `track_b_entry1_qr_filter.py`,
`track_b_entry2_baseline_hierarchy.py`, `track_c_entry1_oracle_headroom.py`.

**Bottom line (see FINDINGS_SUMMARY.md for detail):** across every mechanism family
tested at this session's scale, no computational advantage for the IDM framing over
classical factoring practice was observed. Two threads remain open (utility-conditioned
relation retention; real multi-polynomial routing headroom) pending materially larger
engineering investment, explicitly gated behind a cheaper distribution study that has
not yet been run.
