# Structured Paper Reading Note (Template)

## 1. Metadata & Ledger Summary
- **Title**: `<Exact Title>`
- **Authors / Venue / Year**: `<First Author et al., Venue YYYY>`
- **Category**: `HSI-MSI` / `Vision-Agent` / `Agent+HSI-MSI`
- **Evidence Depth**: `[Full-Text Verified]` / `[Abstract-Level Triage]`
- **Official Code**: `<URL or N/A>`
- **Research Role**: `Baseline` / `Agent Tool Candidate` / `Inspiration` / `Related Work Only`

## 2. Core Problem & Method Essence (3–5 Bullets)
- **Problem Targeted**: `<What specific failure mode or setting does it tackle?>`
- **Core Mechanism**: `<Concise explanation of the architecture / physical prior / agent loop>`
- **Degradation & Spectral Strategy** *(if HSI-MSI)*: `<Known vs. Blind PSF/SRF; how C bands are modeled>`
- **Agent State / Action / Reflection** *(if Agent)*: `<What it observes, which tools it calls, how it stops>`

## 3. Experimental Setup & Verified Results
- **Datasets & Scales**: `<e.g., CAVE x8, Chikusei x8, WorldView-3 full-res>`
- **Key Reported Metrics**: `<Exact numbers from paper tables, or 'Not read' if abstract-only>`
- **Compute / Latency Notes**: `<Params, FLOPs, GPU memory, or Agent turns/sec if reported>`

## 4. Critical Limitations (Why We Can Beat It)
1. `<Limitation 1 — e.g., assumes known SRF and ideal alignment>`
2. `<Limitation 2 — e.g., high inference latency or RGB-only critic>`

## 5. Ready-to-Use Related Work Blurb
> `<1–2 objective academic sentences summarizing the paper's contribution and exact limitation relative to Agent + HSI-MSI fusion.>`
