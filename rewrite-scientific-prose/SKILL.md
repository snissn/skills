---
name: rewrite-scientific-prose
description: Diagnose and substantially rewrite scientific or technical prose that is accurate but hard to read. Use for opaque abstracts, abrupt or awkward introductions, choppy papers or reports and failed humanizer edits; repair scientific context, contribution hierarchy, misplaced detail, omitted premises, jargon, claim scope and sentence flow. Preserve evidence and mathematics while restructuring authorized text, then review the whole result for comprehension, prose and fidelity.
---

# Rewrite Scientific Prose

Version 1.5. Map the source, rebuild the argument, review comprehension, prose and fidelity separately, and repair the result. Neither a first draft nor a completed checklist is a finished application. A collection of polished sections is not evidence that a complete paper has converged.

Make a technically capable reader understand the argument without already knowing the author's private vocabulary. Treat factual preservation, reader comprehension and natural connected prose as separate requirements. An accurate passage that can be reconstructed with effort may still fail as writing.

## Establish the task

- Identify audience, purpose, source version, authorized editing span and deliverables. Infer routine details; ask only when a missing answer would change the scientific claim or authorization.
- Distinguish a strict output-length limit from the span of source pages to edit. Read surrounding definitions and theorem statements when the excerpt depends on them.
- Respect audit-only requests. For a repair, deliver actual revised text, not merely advice or an outline.
- Keep repository writes, publication, external messages and experiments within existing authorization. Editorial work does not authorize changing the model or running a research program.
- Use authoritative sources. Keep models, apparatuses and versions distinct; do not import a stronger result from a related construction.
- For a complete paper, thesis or report, read [the full-document workflow](references/full-document-workflow.md). Define the entire deliverable, including appendices, figures, captions, tables and references. Keep separately published supporting material distinct from the text being rewritten. Preserve accepted passages unless integration exposes a concrete inconsistency.

## Read and map before rewriting

Read [the diagnostic catalogue](references/diagnostic-catalogue.md). Use W01–W50 as detection prompts; record observed passages, reader effects, severity, repair and acceptance evidence. Classifications organize findings; they do not certify quality. Explain inapplicability when disposing of a requested check. A previous clean review does not close a new reader complaint: inspect why the earlier evidence missed it.

Create a working claim ledger using [the ledger format](references/claim-ledger.md). Rank the main contribution, dependent results and applications; record the broader question, narrower task, actors, variables and sequence. Distinguish assumptions, design choices, preparation laws, definitions, exact results, approximations, empirical findings and open identifications. Track values, equations, citations, scope, interventions and destinations for moved detail. Record the premises of every consequential reduction, normalization and change of description, and the order of quantifiers in approximation claims. Verify historical claims and gaps; distinguish an unresolved general problem from this paper's chosen task.

For long documents, also map section roles, first definitions, mathematical dependencies and the interfaces between distinct models or regimes. Track the meaning and scope of reused symbols. Record which result each abstract, discussion, caption and conclusion claim relies on. A sentence can be locally accurate yet misleading when carried into another apparatus, normalization or evidence level.

Trace missing explanations to the source. If the mechanism is unspecified, retain the uncertainty. Do not manufacture a plausible mechanism to improve the prose.

If a summary conflicts with explicit definitions, calculations or scope in the same source, resolve the conflict through that evidence and record the correction. Do not preserve an unsupported promotional claim merely because it appeared in the input. If the evidence cannot resolve it, identify the ambiguity.

## Build the reader's entry point

For an introduction, establish why the question matters before asking the reader to learn the proposed machinery. Technical setup and scientific orientation are different jobs: a well-defined apparatus can still be an abrupt opening. Review the first paragraphs separately from the abstract and later sections; neither can retroactively supply missing context or first-use meaning.

- Choose an entry point appropriate to the genre and audience. A research introduction usually begins with a recognizable phenomenon, scientific question or established difficulty, explains the relevant development of understanding, then narrows to the question and contribution of this paper. Use general scientific or historical context when it explains the stakes; distinguish the field's history from the author's project history. A methods subsection or narrowly requested technical explanation may appropriately start with its setup.
- Make background do explanatory work. Explain what earlier results established, what distinction or difficulty follows, and why the present question is worth asking. Avoid empty claims that a topic is important, an unrelated textbook preamble, and an author-by-author catalogue. Do not manufacture a historical story or imply that no one has addressed a problem merely to motivate the paper. Introduce only the background needed to reach its specific question.
- Test the transition into the proposed work: before its first specialized object appears, can the reader say what problem the object is being introduced to address? Move or rewrite the entry point if it only tells the reader what the authors built. Do not repair an abrupt opening by attaching a generic sentence to an unchanged block of specifications.

- Once the scientific question is established, supply the minimal model of the situation before using it: its objects, relationships and operation. Supply the reference frame or other context that gives symbols meaning before introducing a particular labeled state. Explaining a symbol after the example has already used it is too late. Let the reader picture the setup before asking them to reason within it; defer implementation detail until it has a purpose.
- Name what kind of thing the central object is and what the apparatus or procedure does to it. Give foundational technical terms an operational meaning at their first consequential use: what preparation, observable response or mathematical property the term denotes. Familiarity with a word is not evidence that its intended meaning is clear here.
- Introduce the interpretation and relationships of labels, axes, signs and states before asking the reader to calculate or compare them. Explain the coordinate system or reference arrangement, not only one symbol in isolation. Distinguish an input preparation from an output, an axis from a direction of travel, and a conditional result from an unconditional guarantee where those distinctions matter. Use the minimum explanation needed for this audience; do not add a generic textbook preamble.
- Let a motivating example unfold in time. Establish the initial condition and one main sequence before adding alternative branches or controls. State explicitly whether an alternative replaces a step or adds another step; do not make the reader infer the experiment from its expected result. Explain the consequence that creates the paper's problem. A compact list of several correct predictions can still be an unusable introduction.
- State the paper's answer in physical or explanatory terms before listing fields, function spaces, representations or parameters. Connect the concrete example to the proposed mechanism, and introduce formal objects when their job is apparent.
- Preview the contribution hierarchy before deriving its machinery. Explain how a principal result, an ideal construction, a finite approximation or an application depend on one another when relevant; do not make them compete for prominence. The abstract does not discharge the introduction's own responsibility to orient the reader. Explain what the present work adds on the same axis used to describe its predecessors.
- Require each opening paragraph to advance an intelligible question, answer or consequence. A definition that merely replaces one unexplained term with another, or an inventory of accurate specifications, does not perform that job.
- When the user singles out the opening, stabilize it first through the isolated opening review in [the review protocol](references/review-protocol.md). Then propagate its terminology, example and order through the complete authorized excerpt, removing duplication and repairing transitions. Retain passages the user has explicitly accepted unless consistency requires a change.

## Rebuild the explanation

1. Write a private one-sentence answer to the governing question. Rank supporting results and applications below it. Give each paragraph a current explanatory job. Test a technical paragraph by removing or relocating it: if the argument remains intelligible and reaches its result sooner, move it to its derivation or existing source destination. Do not replace a removed inventory with an equally dense prose inventory or impose an arbitrary length target.
2. Order concepts by explanatory dependency. Establish the need for a construction before naming and specifying it; let the need follow from the preceding explanation rather than a repeated purpose announcement. Separate full state, reduced descriptor, preparation ensemble, observation and theorem. Explain which variables define a descriptor, what information is discarded and which premises make that reduction valid. A local descriptor does not automatically describe an entire system; a coordinate change does not add a degree of freedom. State special preparation, uniformity, factorization or averaging assumptions where the passage uses them.
3. Explain one complete case: input, interaction, output, state change, destination of retained information, and subsequent use. Reuse a motivating example until it explains the mechanism. Show the premise supporting the inference and the bridge from operation to effect; a state change alone does not imply lost information, so explain when distinct inputs become indistinguishable in the reported output. Match the mechanism's detail to the genre: identify the variables acted on and the quantities retained. A partial coordinate calculation can create an apparent contradiction if its reconstruction map or invariants are missing; either supply the necessary bridge or move the calculation and explain the physical operation. Merely renaming the desired outcome is insufficient.
4. State interpretive assumptions beside their results. Explain what supplied laws prescribe and what the construction establishes using them; preserve a positive account of the achievement instead of organizing the prose around disclaimers. Distinguish mathematical conditionality from empirical identification. For multiplied probabilities, sequential updates, averaging or cancellation, preserve the necessary joint law and conditioning; correct marginals or balanced inputs alone may not suffice. Retain exact/ideal/approximate qualifiers locally, including in the abstract.
5. Explain a control as an intervention: what changes, what stays fixed, independent of which variables, under which law, and what the contrast tests.
6. Name compared objects, observations and domains. Define counting units and explain the significance of bounds. Preserve normalization and conditioning, including zero-probability cases. Distinguish aggregate or probability-weighted error from pointwise, worst-case or normalized conditional accuracy; division by a small probability can change the guarantee. State what is fixed before requesting an accuracy and what resources may depend on it. Give conventions a reason when they add a conversion burden; use simpler equivalent notation only with a checked translation.
7. Place prior work where it serves the argument. Bring in work that establishes the scientific question or stakes before the proposed construction; reserve detailed comparisons that require knowing that construction for later. Organize both around ideas, findings and their consequences. Do not impose a blanket early-or-late rule or substitute a literature list for general orientation. When moving background forward, consolidate later repetitions while preserving relevant distinctions and citations.
8. Use tables to organize established understanding. Defer construction recipes, auxiliary constants and proof hypotheses when their role can be explained locally and their details located precisely later. Audit repeated explanations across the overview, example and mechanism: retain a return only when it adds a needed layer, and consolidate the rest.
9. Rewrite the abstract from the repaired argument: problem, mechanism, principal result and essential scope. Select the facts that establish that hierarchy. An abstract need not reproduce every field count, formula, history count, approximation parameter or qualification from the body.

Change paragraph count, order, headings, sentences and detail placement as needed. Preserve scientific content, not original paragraph boundaries. Do not delete substantive qualifications for convenience. Record justified relocation and consolidation in the ledger.

## Turn the explanation into connected prose

Read each paragraph continuously, then across its boundaries. Do this after satisfying the content requirements; otherwise the manuscript can become a checklist with sentences attached.

- Keep an intelligible subject or question active as the paragraph develops. Begin from something the preceding sentence has made available, then add a consequence, explanation, contrast or necessary new detail. Reorder sentences when their connection is missing; adding "therefore", "now" or "to this end" cannot supply an unstated relation.
- Check what ordinary wording presupposes. A target needs an established objective or comparison; a requirement needs a reason; a control needs a specified intervention; "this additional outcome" needs a clear relation to the outcomes already described. Name the relevant actor, purpose or relation when it matters, or state the underlying fact directly. Do not replace one empty label with a synonym or invent an agent to satisfy grammar. These words are not banned when their relationships are established.
- Distinguish reporting what happens from announcing what a paragraph will do. Prefer the physical or mathematical statement when a label such as "the target behavior", "the next task" or "the appropriate comparison" adds no meaning. If the author's objective is essential, state who seeks what and why. Preserve the difference between an objective and a demonstrated result.
- Attach scientific status to the claims themselves. Announcing a comparison does not necessarily tell the reader which system a subsequent example describes. Identify the benchmark before stating its predictions, then make the return to the proposed model and its conditions explicit. If the model adds outcomes or changes the protocol, explain their meaning and the condition for agreement at its first claim; do not silently alternate between different outcome sets. When a condition would overload an overview, move its technical statement to the explanation it qualifies and retain the necessary scope locally; do not replace it with an unexplained "specified" or "permitted" label.
- Integrate definitions where the object becomes useful. Avoid a sequence of independent "X is Y" sentences, repeated dictionary resets, or a definition immediately repeated as a purpose statement. Keep technical names stable; vary sentence structure instead.
- Give each paragraph a developing thought rather than an inventory. Combine dependent short sentences when this clarifies explanation, cause, contrast or qualification. Split crowded sentences at real changes of thought. Do not maximize length, force a fixed rhythm, or drop a condition to obtain a smoother sentence.
- After adding a necessary qualification, rebuild the paragraph around its purpose and main claim. State why a condition matters before listing its variables when that improves comprehension. Consolidate repeated matching or scope statements without losing distinctions. Do not solve every omission by appending another sentence to an already crowded paragraph.
- Make transitions carry subject matter. Explain how the next paragraph follows from the preceding result or unresolved question. Repeated task announcements and identical "To do X" openings expose an outline rather than creating continuity.
- Read the revision at normal reading speed. Mark places that require mentally translating a phrase, supplying an unstated purpose, or restarting after an abrupt topic change. Repair the passage as a unit, not only the conspicuous word. Keep introductions to examples and their scientific status intelligible after removing editorial scaffolding.

## Repair vocabulary and local relations

- Expand private noun stacks into explicit relationships before introducing a reusable short term.
- Disambiguate overloaded words such as action, population, state, phase, control, mass, independence, readiness and capture.
- When a prepared resource supplies a variable, explain how it supplies that variable at the level needed here. Avoid presenting an unexplained extra random variable as a physical mechanism.
- Make definitions explanatory rather than circular or equally opaque.
- Assess the burden of a defined term as well as its correctness. Prefer a functional description at entry when a private metaphor or compressed label makes the reader translate; retain necessary technical names consistently. Distinguish a system's physical property, the detector or algorithm's output, and the reduced descriptor used for comparison.
- Give physical actions to systems and mathematical claims to arguments or estimates. Name what an argument bounds.
- Scope words such as unchanged, fixed and conserved to the relevant variables and stage. An identity operation on a reduced state does not imply that the complete physical system is stationary or unchanged.
- Specify independence, conditioning, neutrality and comparisons relationally.
- Keep terminology stable while distinguishing descriptive levels. Do not vary technical names merely to avoid repetition.
- Expand ambiguous slashes and invented compounds into their actual relationships.
- Repair pronouns, parallelism, category errors and comparisons with missing counterparts.
- Use sentence rhythm to express logical hierarchy. Do not enforce a universal word limit or make every sentence a short announcement.
- Remove repetition that adds no understanding; keep reminders that add a new layer.
- Define failure categories and their scoring briefly enough to distinguish a null, a failed operation and an excluded observation. Do not let generic "fault" or "valid" labels carry an unstated selection rule.
- Preserve necessary terminology and calibrated qualifications. Avoid hype, defensive inventories and forced conversational personality.

## Review through three gates

Follow [the review protocol](references/review-protocol.md).

**Comprehension:** Review an introduction's entry point in isolation before the full passage. Give a reader only the revision. Ask what makes the work worth reading, how its narrower task follows, what its main contribution is and how subsidiary results support it. Then ask for the actors, mechanism, variation, state change, assumptions and comparison, with passage evidence. Check both understanding and placement: a correctly explained paragraph can still interrupt the argument. Separate textual support from imported expertise.

**Prose flow:** Give the revision a separate continuous-reading pass. Check natural phrasing, active context, sentence-to-sentence development, paragraph movement, rhythm and unnecessary announcements. Correct reconstruction in the comprehension review is not evidence that this gate passes. When the user asks for smoother writing, recurring choppiness or unresolved presuppositions remain required repairs even if the facts can be understood.

**Fidelity:** Compare with the frozen source. Check claims, equations, bounds, units, citations, conditions, interventions and relocations. Trace reductions to their premises and approximation statements to their metric and quantifier order. Token matching cannot replace scientific judgment.

When fresh subagents are available, give the comprehension reviewer only the revision and neutral audience/task instructions. Give the fidelity reviewer source and revision without the author's intended verdict. Do not leak an answer key. If independent reviewers are unavailable, perform separate passes and disclose that limitation.

Freeze the exact candidate before handing it to reviewers. Record a version or checksum; do not mix a working draft with the reviewed version. Check quoted passages and consequential findings against that candidate before accepting a review verdict.

Use the inventory helper when useful:

    python3 scripts/audit_inventory.py SOURCE REVISED --output REPORT.json

Treat its output as review prompts. Explanations and relocations can legitimately change token inventories; reconcile them in the ledger. A clean inventory does not certify clarity or equivalence.

## Iterate and finish

- Fix every open critical or major defect. Resolve disputes through the source or the reader's interpretation.
- After a material repair, repeat affected review with a fresh reader where possible.
- After local repairs stabilize, run a fresh review of the complete candidate without the prior audit, desired verdict or repair list. Ask openly what still impedes understanding or misstates the source; do not limit the reviewer to confirming old fixes. Recheck structure and flow after compression as well as after expansion.
- For a full document, assemble it before this review and require explicit coverage of every component. Include a continuous beginning-to-end reading and a separate check of long-range consistency. Section reviews, clean inventories and an accepted introduction cannot substitute for these. After integration repairs, freeze a new candidate and renew the affected technical review and complete-document reading; distinguish partial coverage from full coverage honestly.
- Give every requested audit item a concrete disposition: resolved with evidence, inapplicable with reason, or unresolved with its precise obstruction. Relocation counts only when meaning remains accessible and the destination is stated.
- Stop when the whole text has a clear hierarchy appropriate to its purpose, the reader follows it without guessing, prose and fidelity reviews pass, and no relevant critical/major or specifically requested language defect remains. Verify that each material repair improved the passage without creating another omission or repetition. Treat alternative natural phrasings as preferences, not reasons for endless revision; do not declare convergence from an issue count or a single reviewer's approval.
- Do not claim universal perfection from a successful sample. State the scope and nature of reviews actually performed.
- Keep working audits, ledgers and review transcripts outside manuscript prose.
- Deliver the complete revision, a short account of consequential changes, and genuine remaining limitations. For long documents, provide a validated file and enough text in chat for direct review.
