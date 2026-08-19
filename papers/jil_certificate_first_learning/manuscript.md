# Certificate-First Mathematical Learning: A Coq-Grounded IDM-Readout Architecture for AI-Assisted Mathematics Education

**Article type:** Technical Article

**Target journal:** Journal of Innovative Learning (JIL), Institute for Innovative Learning, Mahidol University

**Word count:** 4659

**Abstract.** Generative artificial intelligence can produce mathematically fluent text without providing a warrant for the claims it presents. This technical article develops Certificate-First Mathematical Learning (CFML) as a proof-rooted architecture for AI-assisted mathematics education. The design is deliberately constrained: no architectural primitive is introduced unless it can be traced to an axiom-free Coq theorem already present in Information Discrete Mathematics (IDM) or Readout Universe. The resulting architecture has five formally grounded invariants. First, the task and requested readout are declared before authorization, following the IDM Declaration Bound. Second, a verdict is treated as a readout relative to a declared threshold or route rather than as the mathematical object itself, following the Readout Universe threshold theorems and IDM equivariant-readout results. Third, exact identities and certified finite bounds are distinguished from unsupported outputs by proof type, using IDM's certified finite-readout theorems. Fourth, unresolved status is kept distinct from determinate neutrality, using the axiom-free four-valued readout-minimality results. Fifth, provenance is retained rather than collapsed, following the injective retained-difference core. CFML therefore treats a language-model response as an untrusted candidate; only a theorem-linked evidence packet may authorize a learner-facing EXACT or CONDITIONAL verdict, while absent or mismatched evidence yields HOLD. The article provides a theorem-to-architecture ledger, a system-concept mapping, and Coq-rooted worked cases. It does not claim that Coq proves learning effectiveness; educational outcomes remain an empirical question for subsequent studies. The contribution is a formally disciplined learning architecture in which generative fluency and epistemic authorization are separated by construction.

**Keywords:** AI-assisted mathematics, formal verification, Coq, certificate-first learning, Information Discrete Mathematics, readout

## 1. Introduction

Generative artificial intelligence has changed the practical conditions of mathematical learning. A learner can obtain a worked solution, an explanation, a reformulation, or a proposed proof within seconds. The educational difficulty is that linguistic completeness and mathematical warrant are not the same property. A response can look finished while containing a local arithmetic error, an invalid transformation, an unverified approximation, or an assumption that was never declared. In such a setting, the central design problem is not simply how to generate better explanations. It is how to prevent the act of generation from being mistaken for the act of authorization.

Research on mathematical language models has already moved toward this separation. Verifier-guided problem solving, program-aided reasoning, external execution, and formal theorem-proving environments all treat generation and checking as distinguishable operations (Cobbe et al., 2021; Gao et al., 2023; Yang et al., 2023). Educational deployment adds a further requirement: the checking relation should not remain hidden inside a back end. Learners should be able to see what kind of evidence supports a mathematical claim, what assumptions that evidence depends on, and when the system refuses to authorize a conclusion.

This article develops Certificate-First Mathematical Learning (CFML) from two existing roots only: Information Discrete Mathematics (IDM) and Readout Universe (Lahtee, 2026a, 2026b). This restriction is methodological, not rhetorical. The architecture is not allowed to acquire a new conceptual component merely because it appears pedagogically attractive. Each invariant admitted into the formal core must be linked to an existing Coq theorem whose axiom profile is reported as closed under the global context. Claims tagged elsewhere as narrative bridges, open conjectures, finite diagnostics, or theorem statements with undeclared classical assumptions are not used as foundations here.

The architecture therefore begins from a smaller question than a general theory of AI tutoring: What is the minimum proof-grounded control structure required before an AI-generated mathematical response may be presented as an authorized result? The answer developed here is a declaration gate, a route-and-certificate gate, a typed evidential standing, and a proof-transparent feedback readout. The language model is intentionally outside the trusted kernel. It may generate candidates, questions, or explanations, but it does not decide the mathematical standing of its own output.

Four contributions are made. First, the paper introduces a root-constrained design methodology in which every architectural invariant is accompanied by an explicit Coq lineage. Second, it derives a declaration-before-authorization gate from the IDM Declaration Bound rather than treating prompt interpretation as an informal pre-processing step. Third, it separates exact, certified-bounded, and unresolved states using IDM's certified finite-readout and readout-minimality theorems. Fourth, it positions learner-facing feedback as a readout of a proof object and declaration record, not as a second unverified explanation. No learning-effect claim is made. Coq establishes the mathematical invariants of the architecture; whether those invariants improve learning must be tested empirically.

## 2. Literature Review

The literature is used here to locate the educational problem, not to generate the architecture's formal primitives. Those primitives come only from the IDM and Readout Coq roots.

### 2.1 Mathematical generation and external verification

Verifier-based mathematical reasoning has repeatedly shown the value of separating candidate production from evaluation. In GSM8K, learned verifiers were used to rank candidate solutions rather than allowing generation alone to determine acceptance (Cobbe et al., 2021). Minerva demonstrated strong quantitative reasoning from technically trained language models while leaving a substantial unsolved set, reinforcing the difference between fluent competence and universal correctness (Lewkowycz et al., 2022). Program-Aided Language Models delegated execution to an external interpreter after the language model generated a programmatic solution path (Gao et al., 2023). LeanDojo placed theorem generation inside a formal Lean environment in which invalid proof terms are rejected by the proof assistant (Yang et al., 2023).

These systems motivate, but do not formally ground, CFML. The distinctive move in this paper is to expose the checking relation as part of the learning interface and to constrain that interface by theorem provenance. A candidate answer is not merely assigned a confidence score. It is paired with a declaration, a route, a certificate type, a source theorem, and a verdict whose meaning is limited by those objects.

### 2.2 AI assistance, substitution, and learner judgment

Educational evidence also warns against equating improved task completion with improved independent learning. Bastani et al. (2025) reported that unrestricted generative-AI assistance could improve performance while the tool was present yet reduce subsequent unaided performance, whereas a more strongly safeguarded tutoring design mitigated much of that cost. Other work shows that structured conversational tutoring can produce positive outcomes when the interaction is designed around learning rather than answer delivery (Henkel et al., 2024). In proof learning, specialized review support has likewise been investigated as an alternative to relying on a general-purpose chatbot alone (Chen et al., 2025).

CFML does not infer from these studies that visible certificates necessarily improve learning. Instead, they justify treating the learner's relation to evidence as an educational design variable worth making explicit. The formal architecture guarantees only that an authorized mathematical readout carries declared provenance. Whether a learner uses that provenance productively is outside the scope of the theorem layer.

### 2.3 Self-explanation and formative feedback as interface context

The self-explanation literature shows that learning involves more than seeing a correct worked answer. Chi et al. (1989) found that successful learners generated explanations connecting solution steps to underlying principles and monitored their own understanding. Technology-enhanced diagnostic systems similarly use structured evidence to determine what kind of feedback should be returned (Panjaburee et al., 2010; Panjaburee & Srisawasdi, 2025). These traditions inform the presentation layer of CFML: evidence should be inspectable and usable for questioning. They do not, however, license a claim that the architecture has already produced self-explanation, transfer, or metacognitive gains. Those remain hypotheses for later evaluation.

The gap addressed by this article is therefore narrow. Existing AI-mathematics work often uses verification to improve machine correctness, while educational work studies how feedback structures affect learners. CFML inserts an explicitly theorem-rooted authorization layer between those domains: verification becomes a visible, typed readout whose formal standing can be inspected before any pedagogical interpretation is added.

## 3. Methodology

This study uses root-constrained technical design. The method differs from ordinary conceptual synthesis because a proposed component is rejected unless it has a machine-checked lineage in one of the two designated source systems.

### 3.1 Admission rule for architectural claims

A CFML invariant was admitted only when four conditions were satisfied. First, its source had to be IDM or Readout Universe. Second, the supporting result had to be a Coq theorem with an axiom-free profile, reported as "Closed under the global context" or documented as part of the axiom-free discrete core. Third, the manuscript's wording could not exceed the theorem's scope. Fourth, any move from theorem to educational interface had to be labeled as a design interpretation rather than as a theorem about learners.

This rule excludes several tempting but unsupported claims. CFML does not claim that formal verification creates understanding, that HOLD improves metacognition, that a declaration gate guarantees correct natural-language interpretation, or that a certificate necessarily produces transfer. It also does not import open conjectures or narrative "readout" claims as if they were formal results.

### 3.2 Formal roots

The IDM root contributes four theorem clusters. The Declaration Bound proves, in its finite combinatorial model, that a predeclared threshold query can ignore the streamed tail while a deferred regime that must preserve all possible queries requires linearly growing retained information; the key theorems are `declared_forgets_tail`, `deferred_record_bits`, and `declaration_separation`. The certified-readout root proves exact finite identities and computable bounds, including `geom_certified_identity`, `geom_certified_defect`, `geom_majorant_tail`, and `iter_sq_certified`. The a-priori root supplies structural certification without waiting for observed convergence, including `apriori_multiplicative_contracts`, `apriori_stable`, and `richardson_apriori_stable`. The readout-minimality root proves that determinate neutrality and unresolved bottom are distinct, through `neutral_distinct_from_bottom`, `bottom_unique`, and `neutral_is_not_bottom`. These files explicitly report axiom-free Coq 8.20 proofs (Lahtee, 2026a).

The Readout Universe root contributes two additional clusters. Its local `UPL_Sorites.v` formalizes a monotone world-side quantity and a thresholded knower-side readout. `readout_monotone`, `flip_unique`, `tolerance_violation_iff_flip`, and `threshold_order` establish that the readout's behavior depends on its declared threshold and that the transition belongs to the readout relation rather than to an assumed discontinuity in the underlying graded quantity. Its re-verified `evidence/RD.v` supplies the retained-difference object stratum, including `RD4_succ_inj`, `toNat_inj`, `eval_hom`, and `eqn_transfer`; the repository records this discrete core as axiom-free (Lahtee, 2026b).

### 3.3 Theorem-to-architecture ledger

Table 1 is the formal admission ledger. It is intentionally stricter than a conceptual mapping: every row names a proof root and limits the architectural consequence to what that root can support.

| Invariant | Coq root | Permitted architectural consequence |
|---|---|---|
| Declaration before authorization | `declared_forgets_tail`; `deferred_record_bits`; `declaration_separation` (IDM Declaration Bound) | Freeze the requested readout before evidence is accepted; do not infer semantic correctness beyond the declaration. |
| Readout-relative verdict | `readout_monotone`; `tolerance_violation_iff_flip`; `threshold_order` (Readout Universe UPL) | Retain threshold/tolerance with the verdict; the readout is not context-free. |
| Faithful readout | `equivariant_stabilizer_containment`; `faithful_stabilizer_equality` (IDM Equivariant Readout) | Do not erase distinctions required by the declared transformation structure. |
| Exact certificate | `geom_certified_identity`; `geom_certified_defect` (IDM Certified) | Authorize EXACT by an exact identity in the declared finite domain, not by confidence. |
| Bounded certificate | `geom_majorant_tail`; `iter_sq_certified`; `apriori_stable`; `richardson_apriori_stable` (IDM Certified/A-priori) | Authorize CONDITIONAL here only with a Coq-certified finite bound and retained assumptions. |
| HOLD distinct from determinate neutral | `neutral_distinct_from_bottom`; `bottom_unique`; `neutral_is_not_bottom` (IDM Readout Minimality) | Do not collapse unresolved status into a determinate neutral or zero result. |
| Provenance retention | `RD4_succ_inj`; `toNat_inj`; `eval_hom`; `eqn_transfer` (Readout Universe RD) | Keep declaration/proof histories distinguishable; this is an operational instantiation, not a theorem about pedagogy. |

### 3.4 Validation strategy

The validation in this technical article is proof-level rather than learner-level. The architecture is checked by theorem coverage: every trusted invariant must have a named Coq root, and any function outside that root is marked untrusted or interpretive. A language model is therefore not validated as a theorem prover by this paper. It is modeled operationally as a source of candidate expressions. The trusted kernel begins only when the declaration and evidence route are fixed.

No synthetic student data, simulated effect sizes, or comparative learning outcomes are introduced. The worked cases in Section 6 are theorem instantiations, not experiments. Human-participant research is the next empirical stage, not a hidden premise of the present article.

## 4. Technical Proposals

### 4.1 The trusted core and the untrusted generator

CFML divides the system into an untrusted generative side and a trusted authorization side. The generative side may contain a language model, a learner's own proposed derivation, or both. Nothing on that side is treated as established merely because it is fluent or complete. The trusted side contains only the declaration record, the admissible IDM route, the evidence object, and the theorem-linked verdict.

The central relation is therefore not "AI answer -> feedback" but:

declared readout + candidate + Coq-rooted evidence -> authorized readout.

The candidate may be absent, wrong, or rhetorically persuasive without changing the authorization rule. This is a design constraint. Its mathematical roots are the separation between object and readout in the threshold formalization, the declaration-timing results in IDM, and the proof-carrying exact/bounded results in the certified-readout layer.

### 4.2 Stage 0: Declaration and specification gate

Before any candidate can be authorized, CFML freezes a declaration record containing the mathematical object, requested operation, domain assumptions, target readout, and any tolerance or threshold that changes the meaning of acceptance. The declaration gate does not claim to solve semantic parsing. A natural-language request can still be misunderstood. The guarantee is narrower: later evidence is bound to one explicit declaration rather than being retrofitted after an answer has been generated.

This ordering is rooted in the Declaration Bound. In its formal model, `declared_forgets_tail` proves that a predeclared query depends only on the relevant prefix, while `deferred_record_bits` and `declaration_separation` prove a sharply different information requirement when the query is deferred. CFML does not transfer the theorem's storage complexity directly into a pedagogical effect. It transfers only the control principle that declaration timing changes what information a valid readout must retain.

The Readout Universe threshold theorem `threshold_order` supplies the second reason for freezing the declaration: changing the threshold changes the readout relation. A verdict without its threshold is therefore incomplete as a record.

### 4.3 Stage 1: Route and evidence typing

After declaration, the system selects a route whose proof status is known. In this paper, only two authorization-producing evidence types are admitted.

EXACT evidence is an equality, identity, or exact finite construction established in the declared domain. `geom_certified_identity` and `geom_certified_defect` are canonical examples: they give an exact algebraic relation between a finite geometric readout and its defect.

CONDITIONAL evidence is admitted here only in the narrow sense of a Coq-certified finite bound. It is not a generic label for "probably correct." `geom_majorant_tail`, `iter_sq_certified`, `apriori_stable`, and `richardson_apriori_stable` demonstrate the relevant proof form: a finite output is accompanied by an inequality or computable bound whose assumptions are explicit. Other possible meanings of conditionality are outside the formal scope of this article and therefore cannot authorize a CFML result here.

If no theorem-linked exact identity or certified finite bound is available for the declared route, the system cannot promote the candidate to an authorized answer. It returns HOLD.

### 4.4 Stage 2: Typed standing and the role of HOLD

HOLD is not a low confidence score. It is an unresolved readout state. The distinction matters because IDM's `IDM_ReadoutMinimality.v` proves that a determinate neutral value and unresolved bottom are not the same object. `neutral_distinct_from_bottom` proves their inequality; `bottom_unique` characterizes bottom as the unique least element in the information order; and `neutral_is_not_bottom` proves that determinate neutrality carries information that bottom does not.

CFML imports this distinction conservatively. It does not identify the entire four-valued algebra with educational correctness. It uses only the theorem-backed separation: "determinate" and "unresolved" may not be collapsed into one symbol without losing information. Accordingly, a result that is exactly neutral, zero, or otherwise determinate is not treated as HOLD, and HOLD is not rendered as if it were a weakly supported numerical answer.

The learner-facing vocabulary remains EXACT, CONDITIONAL, and HOLD because those labels match the IDM solver discipline. Internally, however, the evidence packet carries the theorem name, assumptions, declaration, and proof type. The visible three-state readout is therefore a projection of a richer provenance record, not the ontology of the proof system itself.

### 4.5 Stage 3: Provenance retention

CFML requires that the declaration and the evidence route remain attached to the verdict. This is a design instantiation of the retained-difference discipline rather than a claim that the educational architecture is logically entailed by arithmetic. In Readout Universe's `RD.v`, `RD4_succ_inj` formalizes injective retention at the successor level, while `toNat_inj` and the evaluation-transfer theorems preserve distinguishability across representations. The operational consequence adopted here is simple: two differently declared tasks or proof routes must not be silently merged into one provenance-free answer record.

This requirement is particularly important for AI-generated prose. A natural-language explanation can paraphrase two routes until they look similar. The evidence packet prevents that paraphrase from erasing the mathematical lineage that authorized the result.

### 4.6 Proof-transparent feedback readout

The feedback layer is restricted to displaying or querying the formal packet: the declaration, route, theorem, assumptions, result, bound where applicable, and verdict. A teacher or interface may turn those objects into questions, but the resulting pedagogical prompt is not itself part of the Coq theorem. This distinction keeps the architecture honest: proof transparency is guaranteed at the record level; learning from that transparency is an empirical hypothesis.

Figure 1 summarizes the architecture and shows the theorem roots beneath the trusted stages.

**Figure 1. Coq-grounded CFML architecture and proof-root lineage.**

### 4.7 System-concept mapping

The JIL system concept can be retained without introducing additional formal primitives. Input is the declared mathematical object. Process is route selection and certificate production. Output is the theorem-linked result and standing. Feedback is the proof-transparent readout of that packet. Environment is the human-AI setting in which the generator remains untrusted and the authorization kernel remains theorem-constrained.

| System component | Theorem-grounded object | Boundary |
|---|---|---|
| Input | Frozen declaration: object, assumptions, threshold/tolerance | Defines what the later proof is about. |
| Process | IDM route + certificate production; LLM candidate remains untrusted | Separates generation from authorization. |
| Output | Result + theorem-linked EXACT / CONDITIONAL / HOLD | Makes mathematical standing explicit without substituting confidence for evidence. |
| Feedback | Visible declaration, theorem, assumptions, bound, and status | Exposes the warrant; no learning effect is claimed by Coq. |
| Environment | Learner + teacher + untrusted generator + theorem-constrained kernel | Keeps human interpretation outside the formal guarantee. |

## 5. Discussion

The revised architecture changes the center of gravity of the paper. CFML is not proposed as a general educational philosophy created around IDM. It is a constrained readout architecture extracted from theorem-bearing structures that already exist in IDM and Readout Universe, then placed in an educational setting with its inferential limits left visible.

The strongest consequence is the separation of generative fluency from epistemic authorization. The language model can remain useful without being trusted. It can propose a factorization, suggest a route, paraphrase a bound, or ask a question, but the status of a mathematical claim is determined by an independently declared proof route. This is close in spirit to verifier-guided AI systems, but CFML makes the warrant part of the learner-facing record and refuses to promote a result when the proof route is absent.

A second consequence is that "I do not know" becomes structurally distinct from "the answer is zero," "the two sides balance," or any other determinate neutral result. This is not justified by a psychological argument. It is inherited from the readout-minimality theorem that separates determinate neutral from bottom. In an educational interface, the distinction prevents absence of authorization from being disguised as a weak answer.

A third consequence is that tolerance is no longer an invisible implementation detail. Readout Universe's threshold theorems show formally that threshold choice changes the readout relation, while IDM's finite-bound theorems make an explicit tolerance mathematically inspectable. Thus a learner-facing conditional result should carry the threshold or bound that makes it conditional. The system should not display "correct" as a context-free label when its proof status is actually conditional on a declared finite envelope.

The architecture nevertheless has strict limits. Coq does not prove that the learner interpreted the declaration correctly, that an AI explanation is comprehensible, that visible provenance reduces overreliance, or that HOLD improves self-regulation. Formal verification can guarantee internal mathematical relations only after the relevant objects have been specified. The specification problem therefore remains: if the wrong mathematical object is declared, a perfectly verified certificate can be irrelevant to the learner's intended question. CFML responds by freezing and exposing the declaration, not by pretending to solve natural-language semantics.

This limitation is a strength for subsequent research because it separates two empirical questions that are often conflated. One question concerns system reliability: does the interface prevent unsupported candidates from being authorized? The other concerns learning: does exposure to declaration, theorem, bound, and HOLD states improve error detection, explanation, transfer, or unaided performance? The present article addresses the first at the level of formal design invariants. The second requires controlled human research.

## 6. Implementation

A minimal CFML implementation can be built directly above the IDM solver and the two formal-root repositories without inventing a new epistemic layer.

### 6.1 Execution sequence

1. Parse the learner request into a provisional mathematical declaration.
2. Expose the declaration fields that affect meaning: object, operation, assumptions, target readout, tolerance, and threshold.
3. Freeze the confirmed declaration before route selection.
4. Treat any learner or LLM solution as an untrusted candidate associated with that declaration.
5. Select an IDM route whose evidence type is formally admitted in the root ledger.
6. Produce an exact proof-linked object or a certified finite bound. If neither is available, issue HOLD.
7. Store the evidence packet with declaration, theorem source, assumptions, result, bound if present, and learner-facing standing.
8. Render feedback from the packet without allowing the prose generator to change the verdict.

The key engineering rule is that the explanation and the authorization record are separate objects. Regenerating prose cannot alter a failed certificate, erase a bound, or convert HOLD into a numerical answer.

### 6.2 Coq-rooted worked cases

The examples below are not benchmark results. Each is a direct use of an already machine-checked theorem pattern.

| Case | Coq root | Standing | Learner-facing readout |
|---|---|---|---|
| Finite geometric readout | `geom_certified_defect` | EXACT | Show the finite sum and exact defect term. |
| Richardson refinement | `richardson_apriori_stable` | CONDITIONAL | Show the finite stability bound and assumptions. |
| Threshold readout | `threshold_order` | Readout-specific | Display the declared threshold because it changes the readout. |
| Neutral vs unresolved | `neutral_is_not_bottom` | Determinate OR HOLD | Render unresolved as HOLD, never as a weak neutral answer. |

The geometric-series case illustrates why "certificate-first" is more than post-hoc answer checking. The exact identity fixes what the finite readout means, and the defect term is carried with the result. A learner may then ask why the defect has that form, but the pedagogical question comes after the mathematical standing has been fixed.

The Richardson case shows the narrower meaning of CONDITIONAL adopted in this paper. The system may present a finite approximation only together with the structural contraction assumptions and proven stability bound. If those assumptions cannot be established for the declared route, the architecture does not downgrade the result to a vague probability. It returns HOLD.

The threshold case illustrates why declaration is part of the evidence packet. The same graded sequence can be read differently at different thresholds, and `threshold_order` formalizes the ordering relation between those readouts. The threshold is therefore not metadata that can be discarded after computation.

The neutral-versus-bottom case is a negative control at the level of status semantics. The formal result rules out collapsing a determinate neutral reading into unresolved bottom. This is exactly the distinction required for a fail-closed educational interface.

### 6.3 Reproducibility and audit

The manuscript should be distributed with a formal-root ledger that names repository, file, theorem, axiom profile, and architectural use for every trusted invariant. The current source repositories already expose verification commands and explicit axiom audits. CFML adds no new foundational theorem in this article; it composes those verified results as architectural constraints. This choice avoids claiming a new Coq proof that has not itself been compiled and audited.

For later empirical evaluation, a technical test harness should inject incorrect candidate answers, missing declarations, mismatched tolerances, and unavailable proof routes, then confirm that the interface cannot authorize them. Such a harness would test implementation conformance to the formal architecture. It would still not establish learning gains. A separate learner study would be required for that question.

## 7. Acknowledgements

The author thanks Walancha for sustained discussion and practical support during the broader research program from which the IDM and Readout formal systems, and subsequently this educational architecture, were developed.

## 8. Declaration of Interest

The author is the creator and maintainer of Information Discrete Mathematics and Readout Universe, the two source systems used to derive the architecture. This relationship is disclosed as a potential non-financial competing interest. No other competing financial interests are declared.

## 9. AI Use Disclosure

OpenAI ChatGPT (GPT-5.6 Sol) was used for literature-discovery support, manuscript structuring, language editing, and document preparation. The architecture itself was constrained to theorem roots already present in IDM and Readout Universe; the AI system was not treated as a source of mathematical authority. No synthetic learner data or fabricated experimental results were generated. The author remains responsible for the manuscript and all claims.

## 10. Code and Materials Availability

The implementation substrate is Information Discrete Mathematics, and the formal epistemic/readout root is Readout Universe. The submission branch includes the manuscript and a formal-root ledger mapping every trusted CFML invariant to named Coq theorems and their stated axiom profiles.

## 11. References

- Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakci, O., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. Proceedings of the National Academy of Sciences, 122(26), e2422633122. https://doi.org/10.1073/pnas.2422633122
- Chen, E., Judicke, S., Beigh, K., Tang, X., Xiao, Z., Li, C., et al. (2025). Generative AI alone may not be enough: Evaluating AI support for learning mathematical proof. arXiv. https://arxiv.org/abs/2509.16778
- Chi, M. T. H., Bassok, M., Lewis, M. W., Reimann, P., & Glaser, R. (1989). Self-explanations: How students study and use examples in learning to solve problems. Cognitive Science, 13(2), 145-182. https://doi.org/10.1207/s15516709cog1302_1
- Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., et al. (2021). Training verifiers to solve math word problems. arXiv. https://arxiv.org/abs/2110.14168
- Gao, L., Madaan, A., Zhou, S., Alon, U., Liu, P., Yang, Y., et al. (2023). PAL: Program-aided language models. Proceedings of the 40th International Conference on Machine Learning, 202, 10764-10799. https://proceedings.mlr.press/v202/gao23f.html
- Henkel, O., Horne-Robinson, H., Kozhakhmetova, N., & Lee, A. (2024). Effective and scalable math support: Evidence on the impact of an AI tutor on math achievement in Ghana. arXiv. https://arxiv.org/abs/2402.09809
- Lahtee, Y. (2026a). Information Discrete Mathematics (Version 1.5.1) [Computer software and formal mathematics repository]. GitHub. https://github.com/morrocwi/information-discrete-math
- Lahtee, Y. (2026b). Readout Universe: A philosophy and logic for grounding claims [Computer software, formal evidence, and research monograph]. GitHub. https://github.com/morrocwi/readout_universe
- Lewkowycz, A., Andreassen, A., Dohan, D., Dyer, E., Michalewski, H., Ramasesh, V., et al. (2022). Solving quantitative reasoning problems with language models. arXiv. https://arxiv.org/abs/2206.14858
- Panjaburee, P., Hwang, G.-J., Triampo, W., & Shih, B.-Y. (2010). A multi-expert approach for developing testing and diagnostic systems based on the concept-effect model. Computers & Education, 55(2), 527-540. https://doi.org/10.1016/j.compedu.2010.02.015
- Panjaburee, P., & Srisawasdi, N. (2025). Technology-enhanced personalized learning environment: Moving forward from the research to practices on science, technology, and mathematics education. Journal of Innovative Learning, 1(1), 19-31. https://il.mahidol.ac.th/jil_systems/index.php/01/article/view/34
- Pichitpornchai, C. (2025). Excel in learning by integrating the system concept, the physiology of learning, and innovative learning. Journal of Innovative Learning, 1(1), 1-12. https://il.mahidol.ac.th/jil_systems/index.php/01/article/view/30
- Yang, K., Swope, A., Gu, A., Chalamala, R., Song, P., Yu, S., et al. (2023). LeanDojo: Theorem proving with retrieval-augmented language models. Advances in Neural Information Processing Systems, 36. https://doi.org/10.52202/075280-0944