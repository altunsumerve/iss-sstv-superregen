#!/usr/bin/env python3
"""Review the indexed recordings without modifying originals.

Writes sample statistics, automatic SSTV decode counts, and a clearly labelled
synthetic positive control. No image found is not proof of no SSTV information.
"""
import argparse
import hashlib
import io
import json
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import signal
from scipy.io import wavfile
import sstv

ROOT = Path(__file__).resolve().parents[1]


def normalized_wav(samples, sample_rate):
    y = samples - samples.mean()
    y = y / max(float(np.max(np.abs(y))), 1e-12) * 0.95
    stream = io.BytesIO()
    wavfile.write(stream, sample_rate, (y * 32767).astype(np.int16))
    return stream.getvalue()


def variants(x, fs):
    yield "raw", x
    filtered = signal.sosfiltfilt(
        signal.butter(4, [900, 2600], fs=fs, btype="bandpass", output="sos"), x
    )
    yield "bandpass", filtered
    _, _, z = signal.stft(filtered, fs, nperseg=512, noverlap=384)
    power = np.abs(z) ** 2
    noise = np.percentile(power, 15, axis=1, keepdims=True) * 1.6
    gain = np.maximum(1 - noise / np.maximum(power, 1e-20), 0.15)
    _, cleaned = signal.istft(z * gain, fs, nperseg=512, noverlap=384)
    yield "spectral_subtraction", cleaned[:len(x)]


def positive_control(output):
    colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255),
              (255, 255, 0), (0, 255, 255), (255, 0, 255), (0, 0, 0)]
    pixels = np.zeros((240, 320, 3), dtype=np.uint8)
    for i, color in enumerate(colors):
        pixels[:, i * 40:(i + 1) * 40] = color
    data = sstv.encode_to_wav(Image.fromarray(pixels), sstv.Mode.ROBOT_36,
                              sample_rate=48000)
    _, samples = wavfile.read(io.BytesIO(data))
    converted = signal.resample_poly(samples.astype(float), 3333, 16000)
    buf = io.BytesIO()
    wavfile.write(buf, 9999, np.clip(converted, -32768, 32767).astype(np.int16))
    images = sstv.decode_from_wav(buf.getvalue())
    for i, image in enumerate(images):
        image.save(output / f"SYNTHETIC_CONTROL_NOT_RF_RECEPTION_{i}.png")
    return {"synthetic": True, "sample_rate_hz": 9999,
            "decoded_images": len(images),
            "complete_images": sum(bool(im.info.get("sstv_complete")) for im in images)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cikti", type=Path, default=ROOT / "analiz" / "ciktilar")
    args = parser.parse_args()
    args.cikti.mkdir(parents=True, exist_ok=True)
    index = json.loads((ROOT / "kayitlar" / "index.json").read_text(encoding="utf-8"))
    report = {"python": platform.python_version(),
              "packages": {name: version(name) for name in ["numpy", "scipy", "sstv"]},
              "recordings": []}
    for entry in index:
        path = ROOT / "kayitlar" / entry["file"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Recording changed: {path.name}")
        fs, raw = wavfile.read(path)
        if raw.ndim != 1 or raw.dtype != np.int16:
            raise ValueError(f"Expected mono int16 PCM: {path.name}")
        x = raw.astype(float) / 32768
        x -= x.mean()
        rail = (raw == -32768) | (raw == 32767)
        row = {"file": entry["file"], "original_name": entry["original_name"],
               "sample_rate_hz": fs, "samples": len(raw), "duration_seconds": len(raw) / fs,
               "rail_samples": int(rail.sum()), "rail_percent": float(rail.mean() * 100)}
        if entry["kind"] == "sstv_test":
            row["automatic_decodes"] = {}
            for label, y in variants(x, fs):
                images = sstv.decode_from_wav(normalized_wav(y, fs))
                row["automatic_decodes"][label] = len(images)
                for i, image in enumerate(images):
                    image.save(args.cikti / f"{path.stem}_{label}_candidate_{i}.png")
        else:
            f, p = signal.welch(x, fs, nperseg=8192)
            mask = (f > 30000) & (f < 52000)
            row["peak_in_30_to_52_khz_hz"] = float(f[mask][np.argmax(p[mask])])
        report["recordings"].append(row)
        print(json.dumps(row, ensure_ascii=True), flush=True)
    report["positive_control"] = positive_control(args.cikti)
    (args.cikti / "review.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if report["positive_control"]["complete_images"] != 1:
        raise RuntimeError("Synthetic control failed; do not interpret negative decode results.")
    print("Synthetic Robot36 control: one complete image decoded.")
    print(f"Report: {args.cikti / 'review.json'}")


if __name__ == "__main__":
    main()
