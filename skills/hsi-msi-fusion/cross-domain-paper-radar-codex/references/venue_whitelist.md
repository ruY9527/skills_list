# Strict 9-Venue Whitelist & DBLP Stream Rules

All radar sweeps strictly restrict primary candidates to these **9 top-tier venues** within the **rolling 24-month window** (`[today - 24 months, today]`):

| Short Name | Full Official Name | Type | Exact DBLP Stream Prefix |
| :--- | :--- | :--- | :--- |
| **CVPR** | IEEE/CVF Conference on Computer Vision and Pattern Recognition | Conference | `streams/conf/cvpr` |
| **ICCV** | IEEE/CVF International Conference on Computer Vision | Conference | `streams/conf/iccv` |
| **ECCV** | European Conference on Computer Vision | Conference | `streams/conf/eccv` |
| **NeurIPS** | Advances in Neural Information Processing Systems | Conference | `streams/conf/nips` |
| **ICLR** | International Conference on Learning Representations | Conference | `streams/conf/iclr` |
| **AAAI** | AAAI Conference on Artificial Intelligence | Conference | `streams/conf/aaai` |
| **TPAMI** | IEEE Transactions on Pattern Analysis and Machine Intelligence | Journal | `streams/journals/pami` |
| **IJCV** | International Journal of Computer Vision | Journal | `streams/journals/ijcv` |
| **TIP** | IEEE Transactions on Image Processing | Journal | `streams/journals/tip` |

## Strict Filtering Rules
1. **No Unrefereed arXiv Masquerading**: Standalone arXiv preprints without confirmed acceptance to one of the 9 venues are excluded from radar shortlists.
2. **No Workshops / Companion Tracks**: Entries matching `workshop`, `companion`, or `findings` are automatically discarded.
3. **No Survey / Benchmark Leakage**: Titles containing `survey`, `review`, `overview`, `benchmark`, `dataset`, or `taxonomy` are excluded by default unless the user explicitly passes `--include-surveys`.
4. **Biennial Coverage**: Any rolling 24-month window naturally captures at least one ICCV (odd years) and one ECCV (even years) edition alongside two cycles of CVPR, NeurIPS, ICLR, AAAI, and continuous journal issues of TPAMI, IJCV, and TIP.
