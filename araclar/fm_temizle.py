#!/usr/bin/env python3
"""
fm_temizle.py - Superrejeneratif alicidan alinan gurultulu SSTV kaydini temizler
ve Robot36 (veya baska SSTV modu) resmini cozmeyi dener.

Kullanim:
    python fm_temizle.py kayit.wav
    python fm_temizle.py kayit.wav --gurultu 0 8        (0-8. saniye arasi sadece hisirti)
    python fm_temizle.py kayit.wav --gurultu-dosyasi hisirti.wav

Ne yapar:
  1. Bant gecirme filtresi: SSTV'nin kullandigi 1100-2400 Hz disini atar.
  2. Gurultu profili: Kartin hisirtisini ogrenir (verilen araliktan, ayri dosyadan
     ya da otomatik olarak) ve spektral cikarma ile sesten dusurur.
  3. Farkli sertlikte birkac temiz versiyon yazar (cikti klasorune).
  4. Her versiyondan SSTV resmi cozmeyi dener (sstv paketi kuruluysa).
  5. Oncesi/sonrasi spektrogramini PNG olarak kaydeder.

Gerekli paketler:
    pip install numpy scipy soundfile matplotlib sstv
"""
import argparse
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

BANT_ALT = 1100.0   # Hz  (SSTV senkron 1200 Hz, renk 1500-2300 Hz)
BANT_UST = 2400.0   # Hz
NPERSEG = 1024
NOVERLAP = 768


def yukle(yol):
    x, fs = sf.read(yol, always_2d=True)
    x = x.mean(axis=1)                     # stereo ise mono yap
    x = x - np.mean(x)                     # DC kaydirmayi sil
    return x.astype(np.float64), fs


def bant_filtresi(x, fs):
    sos = signal.butter(6, [BANT_ALT, BANT_UST], btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x)


def stft(x, fs):
    return signal.stft(x, fs=fs, nperseg=NPERSEG, noverlap=NOVERLAP)


def istft(Z, fs, n):
    _, y = signal.istft(Z, fs=fs, nperseg=NPERSEG, noverlap=NOVERLAP)
    if len(y) < n:
        y = np.pad(y, (0, n - len(y)))
    return y[:n]


def gurultu_spektrumu(Z, t, fs, x_bant, args):
    """Her frekans icin gurultu gucunu tahmin et."""
    P = np.abs(Z) ** 2
    if args.gurultu_dosyasi:
        g, gfs = yukle(args.gurultu_dosyasi)
        if gfs != fs:
            g = signal.resample_poly(g, fs, gfs)
        _, _, Zg = stft(bant_filtresi(g, fs), fs)
        return np.mean(np.abs(Zg) ** 2, axis=1, keepdims=True), "ayri dosyadan"
    if args.gurultu:
        bas, son = args.gurultu
        m = (t >= bas) & (t <= son)
        if m.sum() < 4:
            sys.exit("Gurultu araligi cok kisa ya da kaydin disinda.")
        return np.mean(P[:, m], axis=1, keepdims=True), f"{bas}-{son}. saniyeden"
    # Otomatik: her frekansta zamanin en sessiz %15'lik dilimi = gurultu tabani
    return np.percentile(P, 15, axis=1, keepdims=True) * 1.6, "otomatik (minimum istatistik)"


def spektral_cikarma(Z, N, alfa, taban):
    P = np.abs(Z) ** 2
    kazanc = 1.0 - alfa * N / np.maximum(P, 1e-20)
    kazanc = np.maximum(kazanc, taban)
    # zaman boyunca hafif yumusatma (muzikal gurultuyu azaltir)
    cekirdek = np.ones(3) / 3.0
    kazanc = np.apply_along_axis(lambda g: np.convolve(g, cekirdek, mode="same"), 1, kazanc)
    return Z * kazanc


def normalize(y):
    tepe = np.max(np.abs(y))
    return y / tepe * 0.89 if tepe > 0 else y


def coz(yol, cikti_klasoru, etiket):
    try:
        import sstv
    except ImportError:
        return "sstv paketi yok (pip install sstv) - cozme atlandi"
    try:
        resimler = sstv.decode_from_wav(yol)
    except Exception as e:  # bozuk kayitta kutuphane hata verebilir
        return f"cozulemedi ({e})"
    if not resimler:
        return "resim bulunamadi"
    adlar = []
    for i, r in enumerate(resimler):
        ad = os.path.join(cikti_klasoru, f"resim_{etiket}_{i + 1}.png")
        r.save(ad)
        mod = r.info.get("sstv_mode")
        tam = "tam" if r.info.get("sstv_complete", True) else "yarim"
        adlar.append(f"{os.path.basename(ad)} ({mod}, {tam})")
    return "RESIM CIKTI: " + ", ".join(adlar)


def spektrogram(versiyonlar, fs, yol):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(len(versiyonlar), 1, figsize=(11, 2.6 * len(versiyonlar)), sharex=True)
    for ax, (ad, y) in zip(np.atleast_1d(axs), versiyonlar):
        f, t, S = signal.spectrogram(y, fs=fs, nperseg=1024, noverlap=768)
        m = f <= 3500
        ax.pcolormesh(t, f[m], 10 * np.log10(S[m] + 1e-15), shading="auto", cmap="magma")
        ax.set_ylabel("Hz")
        ax.set_title(ad, fontsize=10)
        ax.axhline(1200, color="cyan", lw=0.5, ls="--")
        ax.axhline(1500, color="lime", lw=0.5, ls="--")
        ax.axhline(2300, color="lime", lw=0.5, ls="--")
    np.atleast_1d(axs)[-1].set_xlabel("saniye")
    fig.suptitle("Kesikli cizgiler: 1200 Hz senkron (mavi), 1500-2300 Hz goruntu bandi (yesil)", fontsize=9)
    fig.tight_layout()
    fig.savefig(yol, dpi=110)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description="Superrejeneratif SSTV kaydi temizleyici")
    p.add_argument("kayit", help="kayit dosyasi (.wav)")
    p.add_argument("--gurultu", nargs=2, type=float, metavar=("BAS", "SON"),
                   help="sadece hisirti olan aralik, saniye (or. 0 8)")
    p.add_argument("--gurultu-dosyasi", help="sadece hisirti iceren ayri bir kayit")
    p.add_argument("--cikti", default=None, help="cikti klasoru (varsayilan: kayit_adi_temiz)")
    args = p.parse_args()

    x, fs = yukle(args.kayit)
    if fs < 8000:
        sys.exit(f"Ornekleme hizi cok dusuk: {fs} Hz. En az 8000 Hz (tercihen 44100/48000) kaydet.")
    cikti = args.cikti or os.path.splitext(args.kayit)[0] + "_temiz"
    os.makedirs(cikti, exist_ok=True)
    print(f"Kayit: {args.kayit}  ({len(x) / fs:.1f} sn, {fs} Hz)")

    x_bant = bant_filtresi(x, fs)
    f, t, Z = stft(x_bant, fs)
    N, kaynak = gurultu_spektrumu(Z, t, fs, x_bant, args)
    print(f"Gurultu profili: {kaynak}")

    versiyonlar = [("1_ham", x), ("2_bant", x_bant)]
    for ad, alfa, taban in [("3_hafif", 1.0, 0.15), ("4_orta", 2.0, 0.08), ("5_sert", 4.0, 0.04)]:
        versiyonlar.append((ad, istft(spektral_cikarma(Z, N, alfa, taban), fs, len(x))))

    print()
    print(f"{'versiyon':<10} SSTV sonucu")
    for ad, y in versiyonlar:
        y = normalize(y)
        yol = os.path.join(cikti, f"{ad}.wav")
        sf.write(yol, y.astype(np.float32), fs, subtype="PCM_16")
        print(f"{ad:<10} {coz(yol, cikti, ad)}")

    sp = os.path.join(cikti, "spektrogram.png")
    spektrogram([(a, normalize(y)) for a, y in versiyonlar], fs, sp)
    print()
    print(f"Temiz dosyalar ve spektrogram: {cikti}{os.sep}")
    print("Resim cikmadiysa: .wav dosyalarini sirayla calip telefondaki Robot36'ya dinlet.")


if __name__ == "__main__":
    main()
