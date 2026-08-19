# Certificate-First Mathematical Learning: An Information Discrete Mathematics Architecture for Verifiable AI-Assisted Education

**Article type:** Technical Article

**Target journal:** Journal of Innovative Learning (JIL), Institute for Innovative Learning, Mahidol University

**Word count:** 4095

**Abstract.** Generative artificial intelligence can produce fluent mathematical explanations while remaining vulnerable to arithmetic, symbolic, and logical error. In education, this creates a design problem: a system may appear pedagogically helpful while providing learners with answers whose evidential status is unclear. This technical article proposes Certificate-First Mathematical Learning (CFML), an architecture in which an AI-generated mathematical response is not treated as an accepted answer until it is paired with machine-checkable or explicitly bounded evidence. The proposal is implemented conceptually through Information Discrete Mathematics (IDM), an open-source mathematical solver that routes declared problem types to exact, certified, or fail-closed computational paths. CFML separates natural-language interpretation from mathematical verification and exposes three learner-facing verdicts: EXACT, CONDITIONAL, and HOLD. The architecture is organized as an input-process-output-feedback-environment system: learners declare a task, the system selects an admissible computational route, an evidence packet is produced, a verdict gate controls what may be asserted, and feedback returns both the result and its warrant. The article specifies the evidence packet, pedagogical interaction patterns, implementation requirements, and limitations. CFML is presented as a technical learning architecture rather than a claim of demonstrated learning gains; its educational effectiveness requires subsequent controlled studies. The contribution is a practical design principle for AI-assisted mathematics: fluency may generate candidate reasoning, but acceptance should be governed by verifiable evidence.

**Keywords:** AI-assisted mathematics, verifiable learning, mathematical reasoning, formative feedback, certificate-first architecture

## 1. Introduction

Generative artificial intelligence has made mathematical help available at a scale that conventional tutoring systems could not easily provide. A learner can ask for a worked solution, an explanation, an alternative method, or an immediate response to an error. Yet the central educational risk is also clear: linguistic fluency and mathematical warrant are different properties. Large language models may decompose a problem plausibly while making a local arithmetic or logical mistake, and a learner may not possess the knowledge needed to detect the mistake. Verification therefore cannot be treated as an optional final check. It is part of the instructional design.

The distinction is especially important in mathematics because the object of learning is not merely a final answer. Mathematical competence includes representing a problem, selecting admissible operations, producing a chain of justification, recognizing constraints, and knowing when a conclusion has not been established. Research on mathematical language models has progressively moved from direct answer generation toward verifier-based selection, program-aided reasoning, external execution, and formal theorem proving (Cobbe et al., 2021; Gao et al., 2023; Yang et al., 2023). These approaches improve the reliability of machine reasoning, but educational use adds a further requirement: evidence should be exposed in a form that supports learner judgment rather than hidden behind a tool call.

This article proposes Certificate-First Mathematical Learning (CFML), a technical architecture for AI-assisted mathematics in which every candidate answer is separated from its evidential status. The architecture uses Information Discrete Mathematics (IDM) as an implementation substrate. IDM is an open-source solver with a unified problem registry, exact and certified computational routes, explicit scope boundaries, and fail-closed behavior. Its current public documentation describes 269 registered problem kinds across 11 domains and three top-level verdict classes: EXACT, CONDITIONAL, and HOLD (Lahtee, 2026). The educational proposal does not depend on the claim that one solver can cover all mathematics. On the contrary, CFML is built around declared limits: when a problem lies outside a certified route, the system should expose that fact.

The design follows the system-concept orientation used by the Journal of Innovative Learning, where educational innovation is considered through input, process, output, feedback, and environment (Pichitpornchai, 2025). In CFML, the input is a learner's mathematical task and declaration of what is being asked; the process is route selection and evidence production; the output is a result plus a verdict; feedback includes evidence, error localization, or a principled refusal; and the environment is the human-AI learning setting in which the learner remains responsible for interpretation and revision.

The article addresses one technical question: How can an AI-assisted mathematics environment be designed so that answer generation and answer acceptance are governed by different mechanisms? The objective is not to report learning gains. It is to specify a reproducible architecture that can later be evaluated experimentally.

## 2. Literature Review

The proposed architecture connects three strands of work: mathematical reasoning with language models, tool-mediated verification, and learning designs that make feedback and self-explanation visible.

### 2.1 Generative mathematical reasoning and verification

Quantitative reasoning remains a demanding setting for language models because a small local error can invalidate an otherwise plausible solution. The GSM8K work showed that verifier-based ranking could improve mathematical problem solving by separating candidate generation from evaluation (Cobbe et al., 2021). Minerva subsequently demonstrated that technical-domain pretraining can substantially improve quantitative reasoning, while still leaving a meaningful portion of problems unsolved (Lewkowycz et al., 2022). These results support a useful architectural distinction: generation can be strong without being sufficient for acceptance.

Later work has made the verifier more explicit. PAL delegates computation to an external interpreter after a language model has translated a problem into executable steps, reducing the need for the model itself to perform every arithmetic operation (Gao et al., 2023). Formal theorem-proving systems provide a stronger form of external constraint because a proof assistant rejects an invalid proof term. LeanDojo, for example, connects language-model theorem generation with a formal Lean environment and a reproducible proof corpus (Yang et al., 2023). At the same time, studies of self-verification caution against assuming that an LLM can reliably judge its own reasoning merely because it can produce a second explanation. Hong et al. (2023) found substantial limitations in model self-verification on logical fallacies, and recent work continues to treat verification as a separate capability rather than a guaranteed by-product of generation (Pan et al., 2026).

CFML adopts the same separation, but changes its educational location. Verification is not only an internal reliability mechanism; it becomes a learner-facing object. The system exposes what kind of evidence supports the answer and whether that evidence is exact, bounded, or insufficient.

### 2.2 AI support and the risk of answer substitution

A learning system can improve task performance without improving independent learning. This distinction is especially relevant for generative AI. In a large field experiment in high-school mathematics, Bastani et al. (2025) found that unrestricted generative-AI assistance improved performance while the tool was available, but could reduce later performance when access was removed; a safeguarded tutor design mitigated much of that negative effect. The result does not imply that generative AI is intrinsically harmful. It shows that interface and feedback design influence whether AI functions as support or substitution.

Evidence from tutoring systems also suggests that AI can be educationally useful when embedded in structured interaction. Henkel et al. (2024) reported positive mathematics outcomes for a conversational tutor deployed in Ghana, while a recent proof-learning study found that specialized proof-review support could be more educationally productive than relying on a general-purpose chatbot alone (Chen et al., 2025). These studies motivate an architecture in which the AI is not simply optimized to produce the fastest correct-looking answer.

A certificate-first design introduces friction intentionally. The learner can still receive explanation and guidance, but the system distinguishes a proposed line of reasoning from a verified mathematical claim. This distinction is compatible with the classic self-explanation literature. Chi et al. (1989) showed that stronger learners generated explanations that connected worked steps to underlying principles and monitored their own understanding more accurately. CFML therefore treats evidence as material for explanation: a certificate should not merely say that the machine is correct; it should reveal enough structure for a learner to interrogate why the answer is acceptable.

### 2.3 Diagnostic and feedback architectures

Technology-enhanced learning research has long used diagnosis and feedback loops to adapt instruction. The concept-effect relationship approach developed diagnostic systems that link assessment outcomes to prerequisite concepts and targeted learning guidance (Panjaburee et al., 2010). More recently, Panjaburee and Srisawasdi (2025) synthesized testing, diagnosis, constructivist learning, and formative assessment into a technology-enhanced personalized learning framework. CFML is narrower in content but similar in systems logic: mathematical evidence becomes a diagnostic signal that can determine the next feedback move.

The difference is that CFML diagnoses the standing of a mathematical claim before it diagnoses the learner. A failed certificate may indicate an algebraic error, a violated domain condition, an incomplete numerical bound, an unsupported transformation, or a problem outside the solver's declared scope. Only after this technical status is known should the interface decide how to formulate educational feedback.

## 3. Methodology

This work uses a technical-design methodology rather than a human-subject experiment. The method consisted of four stages.

First, the design requirements were derived from the literature on mathematical verification, program-aided reasoning, formal proof, and AI-supported learning. The requirements were: separation of generation from validation; explicit problem declaration; machine-readable evidence; fail-closed behavior; learner-visible feedback; and traceability from a claim to the computational route that supports it.

Second, the current IDM implementation was examined as a reference substrate. The manuscript is based on the public repository state available in August 2026. The repository documents a unified `idm.solve()` entry point, 269 registered problem kinds, exact arithmetic over integer/rational structures for supported tasks, certified numerical readouts with declared bounds for selected tasks, and explicit HOLD outcomes when a supported certificate cannot be produced or when a request exceeds declared scope (Lahtee, 2026). The local formal-proof directory additionally documents 194 Coq theorems checked as axiom-free within its stated finite scope. These counts describe the software snapshot; they are not claims that all 269 problem kinds are formally proved.

Third, the architecture was mapped to a learning system using five components: input, process, output, feedback, and environment. Each component was required to expose both computational and pedagogical information.

Fourth, design examples were constructed to illustrate behavior across exact, bounded, and unsupported tasks. These examples are implementation patterns, not an empirical dataset. No student performance, learning gain, or comparative model accuracy is reported. Accordingly, no human-participant ethics approval was required for this technical article.

## 4. Technical Proposals

### 4.1 Certificate-First Mathematical Learning architecture

CFML defines a mathematical response as a pair rather than a sentence:

**candidate response + evidence packet -> verdict.**

A natural-language model may generate the candidate response, but it does not determine the verdict by itself. The verdict is produced by a computational or formal route whose admissibility is declared before acceptance.

The architecture contains six operational stages.

**Stage 1: Task declaration.** The system identifies the mathematical object, requested operation, domain assumptions, and expected form of answer. Ambiguity is not silently resolved when different interpretations would change correctness.

**Stage 2: Route selection.** The declared task is mapped to an available route: exact symbolic computation, exact finite algorithm, certified numerical method, formal proof checker, or no admissible route. Route selection is a scope decision, not a confidence score.

**Stage 3: Candidate generation.** A language model, learner, symbolic engine, or combination of these may propose a solution or intermediate steps. Candidate generation is intentionally permissive because creativity and explanatory variety are useful at this stage.

**Stage 4: Evidence production.** The system requests evidence appropriate to the route. Evidence may be an exact rational result, a factorization identity, a residual equal to zero, an interval enclosure, a proven error bound, a formal proof term, or an explicit reason why certification cannot be completed.

**Stage 5: Verdict gating.** The answer is assigned one of three learner-facing states. EXACT means the result is exact within the declared finite or symbolic domain. CONDITIONAL means the result is usable only with its stated tolerance, bound, model, or scope condition. HOLD means the system withholds acceptance because required evidence is unavailable, the problem lies outside declared scope, or a necessary condition fails.

**Stage 6: Pedagogical feedback.** The interface converts the evidence packet into a learning move. For EXACT, the learner can be asked to explain the invariant or identity that makes the answer exact. For CONDITIONAL, the learner can inspect the bound and decide whether it is adequate for the task. For HOLD, the learner is shown what is missing and may reformulate the problem, supply an assumption, choose a different method, or escalate to a teacher.

This sequence is shown in Figure 1.

**Figure 1. Certificate-First Mathematical Learning architecture.**

### 4.2 Evidence packet

A certificate-first interface should return more than `answer = x`. At minimum, an evidence packet should contain: (a) the normalized task declaration; (b) the computational route; (c) the result; (d) the verdict; (e) the evidence object or bound; (f) assumptions and domain restrictions; (g) unresolved conditions; and (h) a human-readable explanation of why the verdict was issued.

For education, an additional field is valuable: the next-question prompt. Rather than automatically explaining everything, the system can use the evidence to ask a focused question such as 'Which assumption makes this inverse valid?', 'Why does this interval certify the sign?', or 'What information is missing before this equation can be solved exactly?' This preserves a distinction between evidence provision and learner explanation.

### 4.3 System-concept mapping

Table 1 maps CFML to the system concept used in innovative learning.

**Table 1. System-concept mapping of CFML**

| Component | CFML object | Educational function |
|---|---|---|
| Input | Declared problem, assumptions, learner goal | Makes the target of reasoning explicit |
| Process | Route selection, candidate generation, evidence production | Separates fluent reasoning from mathematical validation |
| Output | Result + EXACT / CONDITIONAL / HOLD verdict | Prevents an unsupported answer from appearing equivalent to a certified one |
| Feedback | Evidence, error localization, next-question prompt | Supports revision, self-explanation, and formative dialogue |
| Environment | Learner, AI interface, teacher, solver, formal tools | Keeps responsibility distributed and auditable |

### 4.4 Why three verdicts are preferable to a single confidence score

A scalar confidence score is a weak substitute for mathematical status. A model may be highly confident in a wrong answer, and an exact algorithm may produce a result without any probabilistic interpretation. CFML therefore uses categorical epistemic states tied to evidence. EXACT is not 'very confident'; it indicates that the selected route returns an exact result under its declared domain. CONDITIONAL is not 'medium confidence'; it indicates that the result depends on an explicit bound or condition. HOLD is not 'low confidence'; it is an operational refusal to convert an unverified candidate into an accepted mathematical claim.

This distinction is pedagogically important because it teaches learners to ask a different question. Instead of 'How sure is the AI?', the interface encourages 'What warrants this conclusion?'

### 4.5 Relationship to existing AI-tool architectures

CFML is compatible with verifier models, code execution, computer algebra systems, interval arithmetic, and proof assistants. Its novelty is not a new mathematical verifier. The proposal is the educational orchestration layer that makes route, evidence, and refusal visible and uses them to control feedback. In PAL, an interpreter is used to improve reasoning reliability (Gao et al., 2023). In LeanDojo, a formal environment constrains theorem proving (Yang et al., 2023). CFML generalizes the instructional pattern: whichever verifier is used, its evidence status should become part of the learning interaction.

The architecture is also deliberately plural. One route may be exact over rational numbers, another may use a numerical enclosure, and a third may require a proof assistant. CFML does not collapse these forms of warrant into a single 'correct' label.

## 5. Discussion

The central design claim of CFML is modest but consequential: an AI-assisted mathematics system should not use the same mechanism to generate a response and to authorize that response as mathematically established. This separation is common in high-reliability software and increasingly visible in mathematical AI, but educational interfaces often hide it. A learner typically sees one polished response even when the underlying evidential situation is heterogeneous.

Making verdicts explicit may support several forms of learning. EXACT can direct attention to invariant structure and exact transformation. CONDITIONAL can introduce learners to tolerances, approximations, modeling assumptions, and the difference between a numerical answer and a bound on that answer. HOLD can normalize a mathematically legitimate state that conventional chat interfaces tend to suppress: there are occasions when the correct action is to refrain from claiming a result.

The HOLD state is particularly important for AI literacy. If an educational system always produces an answer, learners are trained to interpret completion as competence. A fail-closed architecture teaches a different norm: inability to certify is information. This is consistent with findings that unrestricted generative-AI assistance can become a substitute for independent problem solving, whereas stronger guardrails can preserve more of the learning process (Bastani et al., 2025).

However, certification is not equivalent to understanding. A machine-checkable proof or exact computation can be opaque to a learner. CFML therefore requires a pedagogical translation layer rather than displaying raw certificates alone. The evidence packet should support questions, counterexamples, and learner explanation. This is where CFML connects to self-explanation research: the educational objective is not to transfer certainty from the machine to the learner, but to give the learner a reliable object against which reasoning can be tested (Chi et al., 1989).

The architecture also has limits. First, a certificate is only as strong as its specification. If the wrong problem is declared, an exact answer can be exactly irrelevant. Second, many mathematically meaningful tasks cannot be fully certified by a single finite solver. Third, formal proof coverage is expensive and selective. Fourth, the current article does not establish that CFML improves achievement, transfer, metacognition, or long-term retention. Those are empirical questions.

A suitable next study would compare a conventional LLM tutor with a certificate-first tutor on matched mathematical tasks. Primary outcomes should include not only immediate correctness but also error detection, explanation quality, transfer to structurally altered problems, and performance after AI support is removed. Such a study would test whether visible evidence changes learning behavior rather than merely system reliability.

## 6. Implementation

The current IDM software provides a concrete route for implementing CFML because its public interface already separates problem kinds and verdict status. A front end can call a single structured entry point, but the educational layer should preserve the route metadata rather than flattening all outputs into prose.

A minimal implementation can be expressed as the following pseudocode:

1. Parse the learner request into a structured mathematical declaration.
2. Ask the learner to confirm any assumption that materially affects the task.
3. Query the solver registry for an admissible kind and its evidence tier.
4. Generate or accept a candidate solution.
5. Run the designated exact, certified, numerical, or formal route.
6. Construct the evidence packet.
7. Issue EXACT, CONDITIONAL, or HOLD.
8. Generate feedback from the evidence packet, not from the candidate answer alone.
9. Log the route and verdict for teacher review or later learner reflection.

Table 2 gives design examples based on documented IDM capabilities.

**Table 2. Illustrative CFML interactions**

| Task | Route | Verdict logic | Learner-facing feedback |
|---|---|---|---|
| Factor x^2 - 5x + 6 | Exact polynomial factorization | EXACT if multiplication reconstructs the original polynomial | Ask the learner to verify why the two roots determine the factors |
| Determine eigenvalues of [[2,1],[1,2]] | Exact linear-algebra route over supported domain | EXACT when characteristic polynomial/eigenvalue computation closes exactly | Ask what matrix symmetry contributes and how the result can be checked |
| Evaluate an integral requiring certified numerics | Certified numerical route | CONDITIONAL with a stated enclosure or proven error bound | Ask whether the declared tolerance is sufficient for the problem context |
| Solve a non-polynomial equation outside the exact symbolic route | Scope gate | HOLD when no complete admissible route is available | Explain the unsupported step and offer a numerical or reformulated route without pretending it is exact |

The current repository documentation also exposes capability descriptions, tests, and formal pointers. This traceability can be used to build a teacher-facing audit view in which each classroom response can be traced from claim to solver kind, implementation, test, and—where available—formal theorem. Such provenance is useful for both educational quality assurance and AI governance.

A production classroom implementation should add three safeguards. First, the natural-language parser must never silently alter domain assumptions. Second, the evidence packet should be stored independently of the explanation so that a persuasive explanation cannot overwrite a failed verdict. Third, the interface should reveal HOLD as a normal result rather than treating it as an error state to be automatically retried until some answer appears.

CFML can be implemented with other mathematical engines as well. The requirement is architectural: the generative layer proposes; an independent admissible route evaluates; the evidence status gates assertion; and the pedagogical layer turns that status into feedback.

## 7. Acknowledgements

The author thanks Walancha for sustained discussion and practical support during the broader development of the research program from which this technical article emerged.

## 8. Declaration of Interest

The author is the creator and maintainer of Information Discrete Mathematics (IDM), the open-source software used as the implementation substrate in this article. This relationship is disclosed as a potential non-financial competing interest. No other competing financial interests are declared.

## 9. AI Use Disclosure

OpenAI ChatGPT (GPT-5.6 Sol) was used for literature-discovery support, manuscript structuring, language editing, and document preparation. No synthetic learner data or fabricated experimental results were generated. All cited sources were checked against publisher, conference, journal, or primary-source records, and the author remains responsible for the accuracy and integrity of the submitted manuscript.

## 10. Code and Materials Availability

The implementation substrate is the public Information Discrete Mathematics repository, version 1.5.1, at https://github.com/morrocwi/information-discrete-math. The journal-specific manuscript source and implementation notes are maintained on the paper branch prepared for this submission.

## 11. References

- Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., & Mariman, R. (2025). Generative AI without guardrails can harm learning: Evidence from high school mathematics. Proceedings of the National Academy of Sciences, 122(26), e2422633122. https://doi.org/10.1073/pnas.2422633122
- Chen, E., Judicke, S., Beigh, K., Tang, X., Xiao, Z., Li, C., Li, S., Luttmer, R., Singh, S., Yampolsky, M., Parikh, N., Zhao, Y., Chen, M., Huang, S., Mohanty, A., Johnson, G., Mackey, J., Lin, J., & Koedinger, K. (2025). Generative AI alone may not be enough: Evaluating AI support for learning mathematical proof. arXiv. https://arxiv.org/abs/2509.16778
- Chi, M. T. H., Bassok, M., Lewis, M. W., Reimann, P., & Glaser, R. (1989). Self-explanations: How students study and use examples in learning to solve problems. Cognitive Science, 13(2), 145–182. https://doi.org/10.1207/s15516709cog1302_1
- Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., & Schulman, J. (2021). Training verifiers to solve math word problems. arXiv. https://arxiv.org/abs/2110.14168
- Gao, L., Madaan, A., Zhou, S., Alon, U., Liu, P., Yang, Y., Callan, J., & Neubig, G. (2023). PAL: Program-aided language models. Proceedings of the 40th International Conference on Machine Learning, 202, 10764–10799. https://proceedings.mlr.press/v202/gao23f.html
- Henkel, O., Horne-Robinson, H., Kozhakhmetova, N., & Lee, A. (2024). Effective and scalable math support: Evidence on the impact of an AI tutor on math achievement in Ghana. arXiv. https://arxiv.org/abs/2402.09809
- Hong, R., Zhang, H., Pang, X., Yu, D., & Zhang, C. (2023). A closer look at the self-verification abilities of large language models in logical reasoning. arXiv. https://arxiv.org/abs/2311.07954
- Lahtee, Y. (2026). Information Discrete Mathematics (Version 1.5.1) [Computer software]. GitHub. https://github.com/morrocwi/information-discrete-math
- Lewkowycz, A., Andreassen, A., Dohan, D., Dyer, E., Michalewski, H., Ramasesh, V., Slone, A., Anil, C., Schlag, I., Gutman-Solo, T., Wu, Y., Neyshabur, B., Gur-Ari, G., & Misra, V. (2022). Solving quantitative reasoning problems with language models. arXiv. https://arxiv.org/abs/2206.14858
- Pan, H., Bao, J., Jiang, H., & Song, Y. (2026). FABSVer: Faster training and better self-verification for LLM mathematical reasoning. arXiv. https://arxiv.org/abs/2605.28389
- Panjaburee, P., Hwang, G.-J., Triampo, W., & Shih, B.-Y. (2010). A multi-expert approach for developing testing and diagnostic systems based on the concept-effect model. Computers & Education, 55(2), 527–540. https://doi.org/10.1016/j.compedu.2010.02.015
- Panjaburee, P., & Srisawasdi, N. (2025). Technology-enhanced personalized learning environment: Moving forward from the research to practices on science, technology, and mathematics education. Journal of Innovative Learning, 1(1), 19–31. https://il.mahidol.ac.th/jil_systems/index.php/01/article/view/34
- Pichitpornchai, C. (2025). Excel in learning by integrating the system concept, the physiology of learning, and innovative learning. Journal of Innovative Learning, 1(1), 1–12. https://il.mahidol.ac.th/jil_systems/index.php/01/article/view/30
- Yang, K., Swope, A., Gu, A., Chalamala, R., Song, P., Yu, S., Godil, S., Prenger, R. J., & Anandkumar, A. (2023). LeanDojo: Theorem proving with retrieval-augmented language models. Advances in Neural Information Processing Systems, 36. https://doi.org/10.52202/075280-0944
