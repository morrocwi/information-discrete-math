# Phase 3 decision record

**Superseded/refined by Phase 3B (see `PHASE3B_CODE_AUDIT.md`):** direct CADO-NFS
source-code tracing (not web-search summaries) confirmed real production
observed-execution feedback exists at GLOBAL/BATCH granularity
(`update_ratio`/`request_more_relations` in `scripts/cadofactor/cadotask.py`) — the
broad framing of Phase 3's open question is now CLOSED AS CLASSICAL. What remains
open is narrower: fine-grained (per-polynomial/per-special-q, own-yield-triggered)
abandon-and-reallocate, not found in three traced code regions but not exhaustively
ruled out (Polysel*Task scheduling and msieve remain unread). The HOLD verdict below
still stands, now on stronger, code-verified grounds.


**Question:** is there reason to build a multi-polynomial (MPQS/SIQS-style) harness?

**Answer: HOLD.**

## Why not NO
Classical adaptive practice does not fully close the search space. One specific,
narrow question (Candidate Gap 1 — live within-run yield feedback for
polynomial-switching, as distinct from Murphy's E-score's pre-computed ranking)
survived an 8-query literature pass including 3 rounds of negative search. A
practitioner-adjacent source explicitly states yield prediction "is hard" — this is
not a solved problem being reinvented.

## Why not YES
1. The cheap falsifier for Candidate Gap 1 requires a real 2-polynomial harness —
   MEDIUM engineering cost, not free, not yet built.
2. Our own strongest adjacent evidence (Track C, Entries 008/009: median oracle
   headroom 0% for region-choice-within-one-polynomial, outliers traced to
   unpredictable sampling noise) suggests this class of live-feedback routing tends
   to hit a chicken-and-egg problem: the signal that would justify switching often
   isn't available until most of the cost is already paid. This does not prove
   Candidate Gap 1 is dead (a different polynomial carries real structural signal
   that same-polynomial regions don't), but it is a reason for caution, not
   optimism.
3. Search depth this pass was shallow (web search summaries, no full papers or
   source code read end-to-end) — a deeper primary-source check (CADO-NFS/msieve
   implementation code) is cheaper than building a new harness and should happen
   first if this thread is pursued further.

## What would change this to YES
Reading CADO-NFS/msieve's actual polynomial-selection and sieving source/docs
directly (not summaries) and finding no live-feedback mid-run polynomial-switching
mechanism there either, combined with a decision that the MEDIUM engineering cost of
a 2-polynomial synthetic test is justified given the admitted "yield prediction is
hard" gap.

## What would change this to NO
Finding, in a deeper primary-source read, that CADO-NFS/msieve (or another
established implementation) already does exactly this (monitors early per-polynomial
yield and reallocates effort) — which would fully close Candidate Gap 1 as
classical, not residual.

## Programme status (unchanged beyond what Phase 3 is licensed to touch, per review
## point 35 — only HOLD areas may move)

| Family | Status | Changed this phase? |
|---|---|---|
| RSA-08 (certificate-based pruning) | BLOCK | No |
| RSA-04 (RRR Gate) | DRIFT | No |
| RSA-05 (Cost Fold) | No advantage shown | No |
| Region-choice routing | BLOCK | No |
| B5a (post-acquisition retention) | BLOCK | No |
| B5b (feedback-conditioned acquisition) | HOLD | Refined: specific candidate (polynomial-level live-yield feedback) identified, still HOLD pending deeper prior-art read |
| Sieve-efficiency mechanism space | HOLD | Refined into the Classical Adaptive Map above; largely CLASSICAL (Murphy's E, large-prime variation, filtering), one narrow residual candidate remains |
| Multi-polynomial engineering investment | **new: HOLD** | This phase's own verdict |

No object has been registered in Toledo. No canonical code assigned. No theorem
formalized. This remains a discovery/audit phase per review point 34.
