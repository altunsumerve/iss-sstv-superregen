#!/usr/bin/env python3
"""
sondurme_fm.py - 200 kHz'lik kisa kayitlarda (ESP sayfasindaki H1/H2/H3) kartin
sondurme (quench) sinyalinin, gonderilen FM tonunun ritmiyle titreyip titremedigini olcer.

Fikir (Neal Brown patenti US3337807A, ZL1BTB): super-rejeneratif alicinin kendi kendine
sondurme frekansi, gelen FM sinyaline gore hafifce degisir. Bu degisim yakalanabilirse
egim dedeksiyonundan daha iyi FM cozulur.

Kullanim:
    python sondurme_fm.py h1_pi_kapali.wav h3_fm_ton.wav [--ton 2304]

Cikti: sondurme frekansi, anlik frekans titremesinin tona denk gelen gucu (dB, rastgele
frekanslardaki medyana gore) ve p degeri (rastgele frekanslarin kacinin bu kadar guclu oldugu).
Ayrica Pi'nin ESP kablolarina dogrudan kacan sinyalini (52-60 kHz) kontrol eder.
"""
import argparse

import numpy as np
import soundfile as sf
from scipy import signal

SIZINTI = (52560, 54860, 59470)   # Pi sizintisinin daha once gorulen cizgileri (Hz)


def analiz(yol, ton, rng):
    x, fs = sf.read(yol)
    x = x - x.mean()
    F, P = signal.welch(x, fs, nperseg=8192)
    m = (F > 30000) & (F < 52000)
    fq = F[m][np.argmax(P[m])]

    siz = []
    for c in SIZINTI:
        mm = (F > c - 300) & (F < c + 300)
        bg = (F > c - 3000) & (F < c + 3000)
        siz.append(10 * np.log10(P[mm].max() / np.median(P[bg])))

    sos = signal.butter(4, [fq - 8000, fq + 8000], "bandpass", fs=fs, output="sos")
    z = signal.hilbert(signal.sosfiltfilt(sos, x))
    anlik = np.diff(np.unwrap(np.angle(z))) * fs / 2 / np.pi
    anlik = np.clip(anlik[500:-500], fq - 15000, fq + 15000)

    s = anlik - anlik.mean()
    W = np.abs(np.fft.rfft(s * np.hanning(len(s)))) ** 2
    ff = np.fft.rfftfreq(len(s), 1 / fs)

    def guc(c):
        return W[np.abs(ff - c) < 15].max()

    def artefakt(c):           # ESP32 cerceve artefaktlari: fs/512 katlari
        k = fs / 512
        return min(c % k, k - c % k) < 30

    rnd = [c for c in rng.uniform(800, 9000, 600)
           if not artefakt(c) and abs(c - ton) > 100 and abs(c - 2 * ton) > 100][:300]
    R = np.array([guc(c)for c in rnd])
    db = 10 * np.log10(guc(ton) / np.median(R))
    pdeg = (R >= guc(ton)).mean()
    print(f"{yol}: sondurme {fq:.0f} Hz, titreme@{ton:.0f}Hz {db:+.1f} dB (p={pdeg:.2f}), "
          f"Pi sizintisi {', '.join(f'{v:.0f}' for v in siz)} dB")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("kayitlar", nargs="+")
    p.add_argument("--ton", type=float, default=2304.0)
    a = p.parse_args()
    rng = np.random.default_rng(0)
    for k in a.kayitlar:
        analiz(k, a.ton, rng)
    print("Sizinti 3 dB civarindaysa temiz. 10 dB ustundeyse olcum Pi sizintisiyla kirlenmistir.")


if __name__ == "__main__":
    main()
