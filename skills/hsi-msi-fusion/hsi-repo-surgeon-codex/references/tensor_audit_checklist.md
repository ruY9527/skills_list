# HSI-MSI Tensor, VRAM & Spectral Audit Checklist

Check every item below in **Phase 2** when inspecting a third-party repository:

1. **Channel Axis Convention**: Does the repo use PyTorch `(B, C, H, W)` or MATLAB/remote-sensing `(H, W, C)`? Are `.mat` files loaded with transposed axes?
2. **Hardcoded Band Count**: Search for `3`, `31`, `103`, `128`, `4`, `8` hardcoded in Conv/Linear layers, positional embeddings, or GroupNorm (`num_groups` must divide `C` or embedding dim `D`).
3. **Scale-Factor Rigidity**: Does upsampling assume fixed `scale=4` or `scale=8` (e.g., `PixelShuffle(4)`)? Can it handle arbitrary or non-integer scales?
4. **VRAM Explosion Points**:
   - Full spatial self-attention on $512 \times 512$ without windowing.
   - 3D convolutions/attention across $C=128\text{–}224$ bands without subspace compression ($C \to K$, $K \ll C$).
   - Multi-step diffusion ($T=50\text{–}1000$) without latent/subspace projection.
5. **Normalization & Spectral Fidelity**: Does `InstanceNorm` or per-channel normalization destroy relative inter-band spectral ratios (hurting SAM)? Prefer LayerNorm/RMSNorm or residual connections anchored to upsampled LR-HSI.
6. **Data Range**: Are inputs normalized to `[0, 1]`, `[-1, 1]`, or raw 16-bit sensor DN (`[0, 65535]`)? Mismatched normalization silently ruins pre-trained weights.
