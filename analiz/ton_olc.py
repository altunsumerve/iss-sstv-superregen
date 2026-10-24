#!/usr/bin/env python3
"""
ton_olc.py - Bir kayitta test tonunun gurultunun kac dB ustunde oldugunu olcer.

Deney duzeni: kayit basliyor, ilk kisimda verici kapali, belli bir saniyeden sonra
verici (Pi + rpitx) FM ton gonderiyor. Script iki bolumu karsilastirir.

Kullanim:
    python ton_olc.py kayit.wav                       # varsayilan: ton 2304 Hz, gecis 20. sn
    python ton_olc.py kayit.wav --ton 2304 --gecis 20

Not: rpitx testnfm.sh sesi 48 kHz'de calar. 20833 Hz ornekleme hizinda uretilmis
1000 Hz'lik bir ton dosyasi bu yuzden 1000*48000/20833 = 2304 Hz olarak gider.
"""
import argparse

import numpy as np
import soundfile as sf
from scipy import signal


def ton_snr(f, S, ton, maske):
    i = np.abs(f - ton) < 4
    bg = (f > ton - 300) & (f < ton + 300) & (np.abs(f - ton) > 30)
    p = S[i][:, maske].mean(axis=1).max()
    b = np.median(S[bg][:, maske])
    return 10 * np.log10(p / b)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kayit")
    p.add_argument("--ton", type=float, default=2304.0)
    p.add_argument("--gecis", type=float, default=20.0, help="vericinin acildigi saniye")
    a = p.parse_args()

    x, fs = sf.read(a.kayit)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x = x - x.mean()
    f, t, S = signal.spectrogram(x, fs, nperseg=8192, noverlap=4096)
    once = t < a.gecis - 2
    sonra = t > a.gecis + 2
    print(f"{a.kayit}: {len(x) / fs:.1f} sn, {fs} Hz, kirpilma %{100 * np.mean(np.abs(x) > 0.98):.2f}")
    for ton in (a.ton, 2 * a.ton):
        print(f"  {ton:6.0f} Hz  verici kapali: {ton_snr(f, S, ton, once):+5.1f} dB   "
              f"verici acik: {ton_snr(f, S, ton, sonra):+5.1f} dB")
    print("  (0-3 dB = gurultu seviyesi. Olcum ~1.2 Hz genisliginde bir kutuda yapilir;")
    print("   SSTV'nin ~1 kHz'lik bandina cevirmek icin yaklasik 29 dB cikar.)")


if __name__ == "__main__":
    main()
