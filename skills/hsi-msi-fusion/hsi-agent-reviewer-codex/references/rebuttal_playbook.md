# Evidence-Based Rebuttal & Claim-Toning Playbook

1. **Answer Directly in Sentence 1**: Start every rebuttal item with a direct, respectful answer (`We thank Reviewer X... We have added the requested ablation in Table R1...`) rather than defensive excuses.
2. **Never Fabricate Unrun Experiments**: If a requested experiment has not been run yet, clearly mark it as `[TO RUN: exact dataset, baseline, expected metric]` for the user instead of inventing numbers.
3. **Tone Down Overstatements**: Replace "solves blind HSI-MSI fusion completely" with "significantly improves robustness under unknown PSF/SRF shifts on benchmarks X and Y."
4. **Defending Agent Overhead**: Frame runtime honestly—report exact seconds/tile and turn count, and highlight the trade-off (e.g., 2–3x overhead over a static network in exchange for +X dB / -Y deg SAM on unseen compound degradations where static baselines collapse).
5. **Cross-Reference Shared Concerns**: When Reviewer 1 and Reviewer 3 raise overlapping issues, provide a unified quantitative table once and cross-reference it cleanly.
