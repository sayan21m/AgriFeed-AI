"""Small CNN mould screen on 32×32 RGB. Not AFB1 ppb. Not Indian bag labels."""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn

IMG = 32


class MouldCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.fc = nn.Linear(64, 2)

    def forward(self, x):
        h = self.conv(x).flatten(1)
        return self.fc(h)


def make_vision(kind: str = "cnn") -> nn.Module:
    if kind == "cnn":
        return MouldCNN()
    raise ValueError(kind)


def rgb_to_tensor(rgb: np.ndarray) -> torch.Tensor:
    """uint8 HxWx3 → 1x3x32x32 in [0,1]."""
    from PIL import Image

    img = Image.fromarray(rgb.astype(np.uint8)).convert("RGB").resize((IMG, IMG))
    arr = np.asarray(img).astype(np.float32) / 255.0
    ten = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
    return ten


@torch.no_grad()
def predict_mould_proba(model: nn.Module, rgb: np.ndarray) -> float:
    model.eval()
    logits = model(rgb_to_tensor(rgb))
    prob = torch.softmax(logits, dim=1)[0, 1].item()
    return float(prob)


def synthesise_batch(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Clean cakes / green silage vs mould blotches on brown. HSV fails on uniform green fodder."""
    x = np.zeros((n, IMG, IMG, 3), dtype=np.uint8)
    y = np.zeros(n, dtype=np.int64)
    for i in range(n):
        kind = rng.integers(0, 5)
        if kind == 0:  # clean oilcake
            base = rng.integers(90, 160, size=3)
            img = np.clip(base + rng.normal(0, 12, (IMG, IMG, 3)), 0, 255)
            y[i] = 0
        elif kind == 1:  # clean bran / straw
            img = np.clip(rng.normal(180, 20, (IMG, IMG, 3)) * [1.0, 0.9, 0.6], 0, 255)
            y[i] = 0
        elif kind == 2:  # clean green silage / fodder (HSV false positive)
            img = np.zeros((IMG, IMG, 3))
            img[..., 1] = rng.integers(90, 160)
            img[..., 0] = rng.integers(20, 70)
            img[..., 2] = rng.integers(20, 70)
            img = np.clip(img + rng.normal(0, 8, img.shape), 0, 255)
            y[i] = 0
        else:  # mould on brown cake
            base = rng.integers(80, 140, size=3)
            img = np.clip(base + rng.normal(0, 10, (IMG, IMG, 3)), 0, 255)
            for _ in range(int(rng.integers(2, 6))):
                r0, c0 = rng.integers(2, 24, size=2)
                r1, c1 = r0 + int(rng.integers(6, 14)), c0 + int(rng.integers(6, 14))
                tone = rng.choice(["green", "white", "black"])
                if tone == "green":
                    img[r0:r1, c0:c1] = (40, 140, 50)
                elif tone == "white":
                    img[r0:r1, c0:c1] = (230, 230, 220)
                else:
                    img[r0:r1, c0:c1] = (25, 20, 18)
            y[i] = 1
        x[i] = img.astype(np.uint8)
    return x, y
