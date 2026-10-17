# Experiment and Paper Protocol

This document defines the minimum protocol for turning the repository into a reproducible research paper. Every number quoted in the paper must be derivable from a frozen dataset snapshot and a recorded analysis command.

## 1. Research questions

- **RQ1:** What dangerous capabilities and tool-poisoning patterns appear in public MCP server metadata?
- **RQ2:** How precise are heuristic detectors when their candidate flags are human-validated?
- **RQ3:** How do detector outcomes and live-model behaviors vary across categories of risky or poisoned tool descriptions?

## 2. Threat model

| Element | Definition |
|---|---|
| Assets | MCP tool descriptions, server metadata, public repository content, and model/tool-interaction behavior |
| Adversary | An actor who can publish or modify public MCP metadata, tool descriptions, or repository documentation |
| Defender | An MCP client, registry operator, or security reviewer screening tools before use |
| Attacker goals | Induce unsafe tool use, mislead a model, enable data exfiltration, or cause unauthorized actions |
| Out of scope | Executing third-party server code, contacting live server endpoints, exploiting unpatched systems, or publishing weaponizable payloads |

## 3. Data protocol

1. Freeze every registry crawl with a UTC timestamp, raw API responses, crawl metadata, and a SHA-256 digest.
2. Deduplicate per-server records using the documented `isLatest` rule.
3. Record dataset size at each stage: raw entries, unique servers, extracted tool descriptions, and analyzed samples.
4. Store all prompts, detector rules, and analysis scripts under version control.
5. Publish the exact snapshot used for each reported result through Zenodo.

## 4. Detector validation

- Define each detector pattern before sampling.
- Draw a stratified sample across detector categories and confidence bands.
- Use at least two independent annotators for ambiguous cases.
- Record an adjudication decision, rationale, and final label for every sampled item.
- Report precision only with its sample scope; do not extrapolate precision to unsampled categories without a documented statistical justification.
- Report false positives and near misses, not only confirmed positives.

## 5. Metrics

| Metric | Definition | Reporting requirement |
|---|---|---|
| Coverage | Share of the registry represented by the frozen snapshot | Report crawl depth and registry cursor status |
| Candidate rate | Share of items matching at least one detector pattern | Report denominator and detector version |
| Precision | Validated positives / sampled candidates | Report confidence interval and sample size |
| Recall | Detected known positives / all known positives | Only when a verified positive set exists |
| F1 | Harmonic mean of precision and recall | Only when recall is measurable |
| False-positive rate | Incorrectly flagged benign items / all benign sampled items | Report sample composition |
| ASR | Successful live attacks / attempted live attacks | Predefine success criteria before running experiments |
| Refusal rate | Safe refusals or abstentions / attempted live attacks | Use the same denominator as ASR |

## 6. Live-experiment protocol

1. Specify model name, version, provider, decoding temperature, system prompt, and maximum tokens.
2. Predefine the success criterion for each experiment before execution.
3. Run each configuration with a fixed random seed where supported.
4. Repeat each experiment enough times to characterize variability.
5. Log raw model output, tool-call arguments, safety outcome, and adjudication label.
6. Separate exploratory findings from confirmatory experiments.
7. Do not test systems without authorization.

## 7. Reproducibility checklist

- [ ] Dataset snapshot is frozen and hashed.
- [ ] Detector version is recorded.
- [ ] Prompt templates are stored verbatim.
- [ ] Analysis scripts run from a clean environment.
- [ ] Every paper number has a generating script or notebook.
- [ ] Human-labeling guidelines and adjudication rules are published.
- [ ] Confidence intervals or uncertainty estimates accompany key rates.
- [ ] Limitations and sampling bias are stated.
- [ ] Zenodo version DOI is cited for the exact artifact version.
- [ ] Responsible-disclosure policy is included.

## 8. Paper positioning

The paper should be framed as a **registry-grounded, human-validated measurement study of MCP tool-poisoning detectors**, rather than a general claim that all MCP servers are insecure. The central contribution is the combination of:

1. A large, provenance-preserving registry crawl.
2. A transparent detector taxonomy.
3. Human validation of detector candidates.
4. A reproducible protocol connecting metadata analysis to live behavior.
5. An artifact with versioned DOI and re-derivable results.
