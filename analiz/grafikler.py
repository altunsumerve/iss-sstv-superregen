#!/usr/bin/env python3
"""grafikler.py - README'deki grafikleri kayitlar/ klasorundeki WAV'lardan uretir.
Kullanim: python analiz/grafikler.py   (repo kok klasorunden)"""
import os
import numpy as np
import soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import signal

K, G = "kayitlar", "grafikler"
os.makedirs(G, exist_ok=True)
plt.rcParams.update({"figure.dpi": 120, "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
MAVI, TURUNCU, GRI = "#2b6cb0", "#dd6b20", "#718096"


def oku(ad):
    x, fs = sf.read(os.path.join(K, ad))
    return x - x.mean(), fs


def ton_db(x, fs, ton, a, b):
    f, t, S = signal.spectrogram(x, fs, nperseg=8192, noverlap=4096)
    m = (t > a) & (t < b)
    i = np.abs(f - ton) < 4
    bg = (f > ton - 300) & (f < ton + 300) & (np.abs(f - ton) > 30)
    return 10 * np.log10(S[i][:, m].mean(1).max() / np.median(S[bg][:, m]))


# 1) FM ton: verici kapali / acik ortalama spektrum + zaman icinde 2304 Hz
x, fs = oku("fm_ton_dis_sondurme_kapali.wav")
fig, ax = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1, 1.4]})
for (a0, b0), et, c in (((0, 18), "Pi kapalı (0–18 sn)", GRI), ((22, 60), "Pi FM ton gönderiyor (22–60 sn)", MAVI)):
    F, P = signal.welch(x[int(a0 * fs):int(b0 * fs)], fs, nperseg=8192)
    mm = (F > 2200) & (F < 2410)
    ax[0].plot(F[mm], 10 * np.log10(P[mm] / np.median(P[mm])), color=c, lw=1.2, label=et)
ax[0].axvline(2304, color=TURUNCU, ls=":", lw=1)
ax[0].text(2306, ax[0].get_ylim()[1] * 0.95, "2304 Hz", color=TURUNCU, va="top")
ax[0].set_xlabel("Frekans (Hz)"); ax[0].set_ylabel("Güç / medyan (dB)")
ax[0].legend(frameon=False, fontsize=8, loc="lower left")
ax[0].set_title("Ortalama spektrum")
f, t, S = signal.spectrogram(x, fs, nperseg=8192, noverlap=6144)
i = np.argmin(np.abs(f - 2304)); bg = (f > 2000) & (f < 2600) & (np.abs(f - 2304) > 30)
r = 10 * np.log10(S[i - 1:i + 2].max(0) / np.median(S[bg], axis=0))
k = np.ones(15) / 15
ax[1].plot(t, r, color=GRI, lw=0.6, alpha=0.6)
ax[1].plot(t, np.convolve(r, k, "same"), color=MAVI, lw=2)
ax[1].axvline(20, color=TURUNCU, ls="--", lw=1)
ax[1].text(20.5, ax[1].get_ylim()[1] * 0.95, "Pi FM ton başladı", color=TURUNCU, va="top")
ax[1].set_xlabel("Zaman (sn)"); ax[1].set_ylabel("2304 Hz / gürültü (dB)")
ax[1].set_title("2304 Hz zaman içinde")
fig.suptitle("Kart FM tonu alıyor: 2304 Hz'de zayıf ama gerçek bir çizgi")
fig.tight_layout(); fig.savefig(f"{G}/1_fm_ton.png"); plt.close(fig)

# 2) Dis sondurme karsilastirmasi
deg = {}
for ad, et in (("fm_ton_dis_sondurme_kapali.wav", "Dış söndürme kapalı"), ("fm_ton_dis_sondurme_100k_30.wav", "100 kHz, %30")):
    x, fs = oku(ad)
    deg[et] = (ton_db(x, fs, 2304, 0, 18), ton_db(x, fs, 2304, 22, 60))
fig, ax = plt.subplots(figsize=(7, 4))
w = 0.35; xs = np.arange(len(deg))
ax.bar(xs - w / 2, [v[0] for v in deg.values()], w, color=GRI, label="Ton yokken")
ax.bar(xs + w / 2, [v[1] for v in deg.values()], w, color=MAVI, label="Ton varken")
for j, v in enumerate(deg.values()):
    ax.text(j - w / 2, v[0] + 0.2, f"{v[0]:+.1f}", ha="center"); ax.text(j + w / 2, v[1] + 0.2, f"{v[1]:+.1f}", ha="center")
ax.set_xticks(xs, list(deg.keys())); ax.set_ylabel("2304 Hz / gürültü (dB, ~1.2 Hz kutu)")
ax.set_title("Dış söndürme sinyalin gürültüye oranını değiştirmedi")
ax.legend(frameon=False); ax.set_ylim(0, 8)
fig.tight_layout(); fig.savefig(f"{G}/2_dis_sondurme.png"); plt.close(fig)

# 3) SNR butcesi: ne var, ne lazim
olc = deg["Dış söndürme kapalı"][1]
bant = olc - 10 * np.log10(1000 / 1.22)
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.barh(["Robot36 için gereken", "Ölçülen (Pi antenin dibinde)"], [10, bant], color=[GRI, TURUNCU])
ax.axvline(0, color="k", lw=0.8)
ax.text(bant - 0.5, 1, f"{bant:+.0f} dB", va="center", ha="right", color="w", fontweight="bold")
ax.text(10.5, 0, "+10 dB", va="center")
ax.annotate("", xy=(10, 0.5), xytext=(bant, 0.5), arrowprops=dict(arrowstyle="<->", color="k"))
ax.text((10 + bant) / 2, 0.62, f"~{10 - bant:.0f} dB eksik", ha="center")
ax.set_xlabel("SSTV bandında (~1 kHz) sinyal / gürültü (dB)")
ax.set_xlim(bant - 5, 18)
ax.set_title("SSTV için sinyal çok zayıf")
fig.tight_layout(); fig.savefig(f"{G}/3_snr_butcesi.png"); plt.close(fig)

# 4) 200 kHz spektrum: sondurme cizgisi + Pi sizintisi
fig, ax = plt.subplots(figsize=(9, 4))
for ad, et, c in (("h3_fm_ton_200k_sizintili.wav", "Pi yakında (sızıntılı)", TURUNCU), ("h3_fm_ton_200k.wav", "Pi uzakta (temiz)", MAVI)):
    x, fs = oku(ad)
    F, P = signal.welch(x, fs, nperseg=4096)
    ax.plot(F / 1000, 10 * np.log10(P), color=c, lw=1, label=et)
ax.set_xlim(20, 70); ax.set_xlabel("Frekans (kHz)"); ax.set_ylabel("Güç (dB)")
ax.annotate("kartın söndürme\nfrekansı ~42–44 kHz", xy=(43.5, ax.get_ylim()[1] - 8), ha="center")
ax.annotate("Pi'nin ESP kablolarına\nkaçan sinyali", xy=(56, ax.get_ylim()[1] - 8), ha="center", color=TURUNCU)
ax.legend(frameon=False, loc="upper left")
ax.set_title("200 kHz kayıt: söndürme sinyali ve test vericisinin sızıntısı")
fig.tight_layout(); fig.savefig(f"{G}/4_sondurme_sizinti.png"); plt.close(fig)

# 5) SSTV denemesi spektrogrami
x, fs = oku("sstv_fm_deneme.wav")
f, t, S = signal.spectrogram(x, fs, nperseg=1024, noverlap=768)
m = f < 3500; Z = 10 * np.log10(S[m] + 1e-15)
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.pcolormesh(t, f[m], Z, shading="auto", cmap="magma", vmin=np.percentile(Z, 5), vmax=np.percentile(Z, 99.5))
for y, c in ((1200, "c"), (1500, "lime"), (2300, "lime")):
    ax.axhline(y, color=c, lw=0.6, ls="--")
ax.set_xlabel("Zaman (sn)"); ax.set_ylabel("Frekans (Hz)")
ax.set_title("FM SSTV denemesi: 1200 Hz senkron ve 1500–2300 Hz görüntü bandında iz yok")
fig.tight_layout(); fig.savefig(f"{G}/5_sstv_denemesi.png"); plt.close(fig)

# 6) Otodin testi: 3994 Hz cizgisi Pi'den bagimsiz
x, fs = oku("otodin_islik_test.wav")
f, t, S = signal.spectrogram(x, fs, nperseg=4096, noverlap=3072)
m = (f > 300) & (f < 4900); Z = 10 * np.log10(S[m] + 1e-15)
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.pcolormesh(t, f[m], Z, shading="auto", cmap="magma", vmin=np.percentile(Z, 5), vmax=np.percentile(Z, 99.8))
for x0, et in ((0, "Pi kapalı"), (20, "437.500 MHz"), (40, "437.501 MHz")):
    ax.axvline(x0, color="w", ls="--", lw=0.8); ax.text(x0 + 0.5, 4750, et, color="w", va="top")
ax.set_xlabel("Zaman (sn)"); ax.set_ylabel("Frekans (Hz)")
ax.set_title("Otodin testi: 3994 Hz çizgisi Pi'yi açıp frekansını kaydırınca değişmiyor")
fig.tight_layout(); fig.savefig(f"{G}/6_otodin_testi.png"); plt.close(fig)
print("grafikler/ klasorune 6 grafik yazildi, olculen:", deg, "bant SNR", round(bant, 1))
