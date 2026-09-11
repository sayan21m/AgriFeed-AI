#!/usr/bin/env python3
"""Train CNN vs HSV on synthetic cake/silage/mould patches. CNN is deployed."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from smartfeed.cv_mould import mould_score
from smartfeed.dl_mould import IMG, make_vision, synthesise_batch

ART = ROOT / "notebooks" / "cv" / "artifacts"
ART.mkdir(parents=True, exist_ok=True)
SEED = 42
EPOCHS = 25


def hsv_flag_batch(x: np.ndarray) -> np.ndarray:
    return np.array([mould_score(im)["flag"] for im in x], dtype=int)


def to_tensor(x: np.ndarray) -> torch.Tensor:
    t = torch.from_numpy(x.astype(np.float32) / 255.0)
    return t.permute(0, 3, 1, 2)


def train_cnn(x_tr, y_tr, x_te, y_te):
    torch.manual_seed(SEED)
    model = make_vision("cnn")
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()
    xt, yt = to_tensor(x_tr), torch.from_numpy(y_tr)
    model.train()
    for _ in range(EPOCHS):
        perm = torch.randperm(len(yt))
        for start in range(0, len(yt), 64):
            idx = perm[start : start + 64]
            opt.zero_grad()
            loss = loss_fn(model(xt[idx]), yt[idx])
            loss.backward()
            opt.step()
    model.eval()
    with torch.no_grad():
        pred = model(to_tensor(x_te)).argmax(1).cpu().numpy()
    return model, pred


def main():
    rng = np.random.default_rng(SEED)
    x, y = synthesise_batch(2400, rng)
    idx = rng.permutation(len(y))
    cut = int(0.8 * len(y))
    tr, te = idx[:cut], idx[cut:]
    x_tr, y_tr, x_te, y_te = x[tr], y[tr], x[te], y[te]

    hsv = hsv_flag_batch(x_te)
    model, pred = train_cnn(x_tr, y_tr, x_te, y_te)
    table = [
        {
            "model": "cnn",
            "acc": float(accuracy_score(y_te, pred)),
            "f1": float(f1_score(y_te, pred)),
            "precision": float(precision_score(y_te, pred, zero_division=0)),
            "recall": float(recall_score(y_te, pred, zero_division=0)),
        },
        {
            "model": "HSV colour screen",
            "acc": float(accuracy_score(y_te, hsv)),
            "f1": float(f1_score(y_te, hsv)),
            "precision": float(precision_score(y_te, hsv, zero_division=0)),
            "recall": float(recall_score(y_te, hsv, zero_division=0)),
        },
    ]
    print(json.dumps(table, indent=2))
    torch.save({"kind": "cnn", "state": model.state_dict()}, ART / "mould_vision.pt")
    metrics = {
        "model": "hsv + cnn",
        "test": table,
        "deployed": "cnn",
        "hsv_vs_dl": {
            "note": (
                "Held-out synthetic 32x32 patches: clean cake, clean bran, "
                "uniform green silage (HSV false-positive), and mould blotches on brown. "
                "Not Indian bag photos. Not AFB1 ppb."
            )
        },
        "n_train": int(len(y_tr)),
        "n_test": int(len(y_te)),
        "image_size": IMG,
        "public_feed_bag_images": 0,
        "grainset_tiny_skipped_mb": 695,
        "predicts_afb1_ppb": False,
    }
    (ART / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("deployed cnn hsv_acc", table[1]["acc"])


if __name__ == "__main__":
    main()
