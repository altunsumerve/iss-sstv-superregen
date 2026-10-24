# Grafikler / Plots

İlk altı grafik önceki deneylerin görselleridir ve korunmuştur. Başlıklarındaki yorumlar, ana README'deki ölçüm sınırlarıyla birlikte okunmalıdır. Özellikle SNR bütçesi kalibre edilmiş hassasiyet veya kesin Robot36 eşiği değildir.

The first six plots are preserved from earlier experiments. Read their interpretations together with the limitations in the main README. In particular, the SNR budget is not calibrated sensitivity or a definite Robot36 threshold.

| Dosya / File | Konu / Topic |
|---|---|
| [1_fm_ton.png](1_fm_ton.png) | Önceki FM ton analizi / Earlier FM-tone analysis |
| [2_dis_sondurme.png](2_dis_sondurme.png) | Dış söndürme karşılaştırması / External-quench comparison |
| [3_snr_butcesi.png](3_snr_butcesi.png) | Yaklaşık bant genişliği hesabı / Approximate bandwidth extrapolation |
| [4_sondurme_sizinti.png](4_sondurme_sizinti.png) | Söndürme ve sızıntı / Quench and leakage |
| [5_sstv_denemesi.png](5_sstv_denemesi.png) | Önceki SSTV incelemesi / Earlier SSTV review |
| [6_otodin_testi.png](6_otodin_testi.png) | Otodin denemesi / Autodyne experiment |
| [7_sstv_kayit_karsilastirma.png](7_sstv_kayit_karsilastirma.png) | Dört uzun kayıt, aynı ölçek / Four long recordings, same scale |
| [8_kisa_kayit_karsilastirma.png](8_kisa_kayit_karsilastirma.png) | Yedi kısa kayıt / Seven short recordings |
| [9_am_video_spektrumu.png](9_am_video_spektrumu.png) | AM videosunun mikrofon sesi / AM video's microphone audio |
| [sema_dis_sondurme.png](sema_dis_sondurme.png) | ESP32, BC546 ve dış söndürme bağlantısı / ESP32 and BC546 external-quench circuit |
| [sema_otodin.png](sema_otodin.png) | İkinci 10 kΩ potla baz gerilimi ayarı / Base-bias adjustment with the second 10 kΩ potentiometer |

Yeni grafiklerde özgün dosya adları kullanılır; [eşleme tablosu](../kayitlar/README.md) repo adlarını gösterir. 7 numaralı grafikte 1200/1500/2300 Hz çizgileri yalnızca kılavuzdur. 8 numaralı grafikte alttaki eğriler, geniş bir banttan Hilbert dönüşümüyle çıkarılan yaklaşık anlık frekans spektrumlarıdır; tek başlarına FM alım kanıtı sayılmaz.

The new plots use original filenames; see the [mapping table](../kayitlar/README.md). The 1200/1500/2300 Hz lines in plot 7 are guides only. The lower curves in plot 8 are approximate instantaneous-frequency spectra derived with a Hilbert transform over a broad band; they do not by themselves demonstrate FM reception.

Şemalar yeni eklenen deney klasöründen alındı. Otodin şemasının altındaki sürekli osilasyon ifadesi hedefi anlatır; doğrulanmış sonuç değildir. Akım hesabının sınırları [bağlantı rehberinde](../belgeler/baglantilar.md#ikinci-pot) açıklanır.

The diagrams were imported from the supplied experiment folder. The autodyne caption describes the intended continuous oscillation, not a verified outcome. See the [English wiring guide](../belgeler/baglantilar.md#english) for translations and current-estimate limitations.

## Yeniden üretme / Regeneration

Repo kökünden / From the repository root:

```sh
python -m pip install -r requirements.txt -r requirements-diagrams.txt
python analiz/semalar.py
python analiz/grafikler.py
```

İlk betik iki şemayı, ikinci betik ilk altı grafiği yeniden yazar. 7–9 numaralı grafikler bu betiklerle üretilmez. Eski grafik betiğindeki SNR varsayımları yeni ölçümlerle doğrulanmış eşikler değildir.

The first script rewrites the two circuit diagrams; the second rewrites plots 1–6. Neither generates plots 7–9. The older plot script's SNR assumptions are not newly validated decoding thresholds.
