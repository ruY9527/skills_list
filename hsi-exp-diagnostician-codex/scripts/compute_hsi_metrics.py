#!/usr/bin/env python3
"""Compute core HSI-MSI physical/spectral metrics and optional diagnostic plots.

Metrics computed:
  - PSNR (dB, per-band mean & global)
  - SAM (Spectral Angle Mapper, degrees, mean & p95/p99)
  - ERGAS (at user-specified spatial scale ratio)
  - CC (Mean band-wise Pearson Correlation Coefficient)
  - Per-band PSNR/RMSE breakdown & worst-5 bands

Supports `.npy` inputs (and `.mat` if scipy is installed). Plots are generated
if `--plot-dir` is set and matplotlib is available.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore[assignment]


def load_hsi_array(path: str, mat_key: str | None = None, channel_first: bool = False) -> Any:
    if np is None:
        raise RuntimeError("numpy is required to load arrays and compute HSI metrics.")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".npy":
        arr = np.load(path)
    elif ext == ".mat":
        try:
            import scipy.io as sio
        except ImportError as exc:
            raise RuntimeError("scipy is required to read .mat files; convert to .npy or install scipy.") from exc
        mat = sio.loadmat(path)
        keys = [k for k in mat.keys() if not k.startswith("__")]
        key = mat_key if mat_key else (keys[0] if keys else "")
        if key not in mat:
            raise KeyError(f"Key '{key}' not found in {path}. Available keys: {keys}")
        arr = mat[key]
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Use .npy or .mat.")

    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim != 3:
        raise ValueError(f"Expected 3D HSI cube, got shape {arr.shape}")
    if channel_first:
        arr = np.transpose(arr, (1, 2, 0))
    return arr


def compute_metrics(gt: Any, pred: Any, scale: int, data_range: float | None = None) -> dict[str, Any]:
    if gt.shape != pred.shape:
        raise ValueError(f"Shape mismatch: gt={gt.shape} vs pred={pred.shape}")
    h, w, c = gt.shape
    max_val = float(data_range) if data_range else float(max(np.max(gt), 1e-8))
    if max_val <= 1.0 + 1e-3:
        max_val = 1.0

    diff = gt - pred
    mse_per_band = np.mean(diff ** 2, axis=(0, 1))
    rmse_per_band = np.sqrt(np.maximum(mse_per_band, 1e-16))
    psnr_per_band = 20.0 * np.log10(max_val / rmse_per_band)

    mean_psnr = float(np.mean(psnr_per_band))
    global_mse = float(np.mean(diff ** 2))
    global_psnr = float(20.0 * math.log10(max_val / math.sqrt(max(global_mse, 1e-16))))

    # ERGAS
    band_means = np.mean(gt, axis=(0, 1))
    safe_means = np.where(np.abs(band_means) > 1e-8, band_means, 1e-8)
    ergas = float((100.0 / scale) * math.sqrt(float(np.mean((rmse_per_band / safe_means) ** 2))))

    # SAM (degrees)
    dot = np.sum(gt * pred, axis=2)
    norm_gt = np.linalg.norm(gt, axis=2)
    norm_pr = np.linalg.norm(pred, axis=2)
    denom = np.maximum(norm_gt * norm_pr, 1e-12)
    cos_val = np.clip(dot / denom, -1.0, 1.0)
    sam_map_deg = np.degrees(np.arccos(cos_val))
    mean_sam = float(np.mean(sam_map_deg))

    # Band-wise Pearson CC
    ccs = []
    for b in range(c):
        g = gt[:, :, b].ravel()
        p = pred[:, :, b].ravel()
        g_c = g - g.mean()
        p_c = p - p.mean()
        d = math.sqrt(float(np.sum(g_c ** 2) * np.sum(p_c ** 2)))
        ccs.append(float(np.sum(g_c * p_c) / d) if d > 1e-12 else 0.0)
    mean_cc = float(np.mean(ccs))

    worst_band_idx = np.argsort(psnr_per_band)[: min(5, c)].tolist()
    worst_pixel_flat = int(np.argmax(sam_map_deg))
    wy, wx = divmod(worst_pixel_flat, w)

    return {
        "shape_HWC": [h, w, c],
        "scale": scale,
        "data_range": max_val,
        "psnr_band_mean_db": round(mean_psnr, 4),
        "psnr_global_db": round(global_psnr, 4),
        "sam_mean_deg": round(mean_sam, 4),
        "sam_p95_deg": round(float(np.percentile(sam_map_deg, 95)), 4),
        "sam_p99_deg": round(float(np.percentile(sam_map_deg, 99)), 4),
        "ergas": round(ergas, 4),
        "cc_mean": round(mean_cc, 5),
        "worst_5_bands_by_psnr": [
            {"band_idx": int(i), "psnr_db": round(float(psnr_per_band[i]), 3), "rmse": round(float(rmse_per_band[i]), 5)}
            for i in worst_band_idx
        ],
        "worst_sam_pixel_yx": [int(wy), int(wx)],
        "worst_sam_pixel_deg": round(float(sam_map_deg[wy, wx]), 4),
        "_arrays": {
            "psnr_per_band": psnr_per_band,
            "sam_map_deg": sam_map_deg,
            "spatial_mae": np.mean(np.abs(diff), axis=2),
            "worst_gt_spec": gt[wy, wx, :],
            "worst_pred_spec": pred[wy, wx, :],
        },
    }


def save_plots(plot_dir: str, report: dict[str, Any]) -> list[str]:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("Warning: matplotlib not installed; skipping diagnostic plots.", file=sys.stderr)
        return []

    os.makedirs(plot_dir, exist_ok=True)
    arrays = report["_arrays"]
    saved: list[str] = []

    # 1. Spatial SAM error heatmap
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(arrays["sam_map_deg"], cmap="inferno")
    ax.set_title(f"Spatial SAM Map (Mean={report['sam_mean_deg']:.2f} deg)")
    fig.colorbar(im, ax=ax, label="SAM (deg)")
    fig.tight_layout()
    p1 = os.path.join(plot_dir, "spatial_sam_heatmap.svg")
    fig.savefig(p1)
    plt.close(fig)
    saved.append(p1)

    # 2. Band-wise PSNR profile
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(arrays["psnr_per_band"], linewidth=1.6)
    ax.set_xlabel("Spectral Band Index")
    ax.set_ylabel("PSNR (dB)")
    ax.set_title(f"Per-Band PSNR (Mean={report['psnr_band_mean_db']:.2f} dB)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p2 = os.path.join(plot_dir, "bandwise_psnr.svg")
    fig.savefig(p2)
    plt.close(fig)
    saved.append(p2)

    # 3. Worst-SAM pixel spectral curve comparison
    wy, wx = report["worst_sam_pixel_yx"]
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.plot(arrays["worst_gt_spec"], label="GT", linewidth=1.8)
    ax.plot(arrays["worst_pred_spec"], label="Pred", linestyle="--", linewidth=1.6)
    ax.set_xlabel("Spectral Band Index")
    ax.set_ylabel("Reflectance / Intensity")
    ax.set_title(f"Worst-SAM Pixel ({wy}, {wx}) Spectral Curve (SAM={report['worst_sam_pixel_deg']:.2f} deg)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    p3 = os.path.join(plot_dir, "worst_pixel_spectrum.svg")
    fig.savefig(p3)
    plt.close(fig)
    saved.append(p3)

    return saved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute HSI-MSI metrics and generate SVG diagnostic plots.")
    parser.add_argument("--gt", required=True, help="Path to ground-truth HSI (.npy or .mat).")
    parser.add_argument("--pred", required=True, help="Path to reconstructed HSI (.npy or .mat).")
    parser.add_argument("--scale", type=int, default=8, help="Spatial downsampling scale for ERGAS (default: 8).")
    parser.add_argument("--mat-key", default=None, help="Optional variable key when reading .mat files.")
    parser.add_argument("--channel-first", action="store_true", help="Set if input arrays are [C, H, W] instead of [H, W, C].")
    parser.add_argument("--data-range", type=float, default=None, help="Optional max signal value (auto-detected if omitted).")
    parser.add_argument("--plot-dir", default=None, help="Optional directory to save SVG diagnostic plots.")
    parser.add_argument("--output", default=None, help="Optional output JSON report path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if np is None:
        print("Error: numpy is required to run compute_hsi_metrics.py.", file=sys.stderr)
        return 1
    try:
        gt = load_hsi_array(args.gt, mat_key=args.mat_key, channel_first=args.channel_first)
        pred = load_hsi_array(args.pred, mat_key=args.mat_key, channel_first=args.channel_first)
        report = compute_metrics(gt, pred, scale=args.scale, data_range=args.data_range)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    saved_plots: list[str] = []
    if args.plot_dir:
        saved_plots = save_plots(args.plot_dir, report)

    report.pop("_arrays", None)
    report["saved_plots"] = saved_plots

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"Saved HSI metric diagnostic report to {args.output}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
