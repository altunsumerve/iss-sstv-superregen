# Kayıt incelemesi / Recording review — 2026-10-23

[Türkçe özet](../README.md) · [English summary](../README.en.md) · [Sayısal sonuçlar / Numerical results](kayit_olcumleri.json)

## Türkçe

İnceleme 4 uzun SSTV testi ve 7 kısa kontrol/ton kaydını kapsar. [Dosya indeksi](../kayitlar/index.json) özgün adları, örnek sayısını, örnekleme hızını ve SHA-256 özetini içerir. Tüm dosyalar mono 16 bit PCM'dir.

### Yöntem

1. WAV örnekleme hızı ve uzunluğu okundu; DC ortalaması çıkarıldı. Tam ölçek sınırına eşit örnekler (`-32768` veya `32767`) sayıldı. Bu oran, ADC kırpılmasının ayrı bir ölçümü değildir.
2. Uzun kayıtların spektrogramı 512 örneklik pencere ve 448 örnek örtüşmeyle çizildi; tüm dosyalarda renk sınırları aynı tutuldu. Dalga biçimleri görselleştirme için 20 örnekte bir gösterildi; sayısal ölçümler tam veriden yapıldı.
3. Üç otomatik SSTV çözme girdisi kullanıldı: DC'si çıkarılmış ham ses; 4. dereceden 900–2600 Hz Butterworth bant geçiren filtre (`sosfiltfilt`); bu filtreli sesten spektral çıkarma. Son adımda 512/384 STFT, zamandaki %15 güç yüzdeliği × 1,6 gürültü tahmini ve en az 0,15 spektral genlik kazancı kullanıldı. Her girdi 0,95 tepe genliğe normalize edilip 16 bit WAV'a çevrildi.
4. `sstv==0.2.0`, başlık/VIS araması açık ve mod otomatik olacak şekilde çalıştırıldı. 4 × 3 denemede sıfır görüntü döndü. Zorla başlıksız görüntü üretimi başarı kabul edilmedi.
5. Pozitif kontrol için 320 × 240 renkli şeritler Robot36 olarak 48 kHz'de kodlandı, 9999 Hz'e yeniden örneklendi ve çözüldü: bir tam görüntü çıktı. Bu yalnızca yazılım yolunu sınar; orijinal Pi kaynak sesini veya RF zincirini doğrulamaz.
6. Kısa kayıtlarda Welch spektrumu 8192 örneklik pencerelerle hesaplandı. 30–52 kHz aralığındaki tepe 41,7–42,3 kHz arasında bulundu. Bu aralıkta tepe aramak, daha güçlü başka bileşenlerin yok olduğu anlamına gelmez.

Ek JSON'daki çizgi/arka plan oranları, pencere içinde seçilen tepenin yerel medyana oranıdır. En büyük tepeyi seçmek gürültüde de pozitif değer üretir; bunlar istatistiksel anlamlılık veya toplam SNR ölçümü değildir. `sync_rhythm` alanı 6,45–6,85 Hz aralığındaki en büyük değeri arar; tek başına SSTV senkronu tespiti değildir. Kısa kayıtlardaki Hilbert analizi de tek ve temiz bir taşıyıcı varsayımına duyarlıdır.

### Tekrar çalıştırma

```sh
python -m pip install -r requirements.txt
python analiz/kayit_incele.py
```

Komut, dosya özetlerini doğrular ve `analiz/ciktilar/review.json` üretir. Kırpılma sayıları, süreler, kısa kayıtların bant içi tepe konumları, üç çözme denemesi ve sentetik kontrol tekrarlanır. Arşivdeki ek spektral oranlar ve grafikler bu komutla yeniden üretilmez. Betik orijinal WAV dosyalarını değiştirmez.

### Sınırlar

Bu kayıtlar bir hassasiyet kalibrasyonu değildir. Test vericisinin alıcı girişindeki RF seviyesi ve sapması ölçülmedi. Deneyi tekrarlamak için kendi seçtiğiniz bir görseli (`test.png`) Robot36 modunda, 48 kHz örnekleme hızında SSTV sesine (`sstv48.wav`) dönüştürebilir veya aynı modda ve örnekleme hızında hazır bir SSTV test sinyali kullanabilirsiniz. Kayıtlar, devrede farklı zamanlarda yapılan değişikliklerin ardından alınmıştır. Bu değişiklikler proje dosyalarında açıklanmıştır. Başarısız otomatik çözüm; hiç bilgi olmadığı, başka bir çözücünün de kesin başarısız olacağı veya devrenin hiçbir değişiklikle çalışamayacağı anlamına gelmez.

## English

The review covers four 60-second SSTV tests and seven approximately 0.145-second control/tone recordings. All are mono 16-bit PCM. The [index](../kayitlar/index.json) preserves original names and SHA-256 hashes.

- Full-scale counts include samples exactly equal to -32768 or 32767. Firmware applies digital gain and clipping, so this is not an independent ADC-overload measurement.
- Long-recording spectrograms use 512-sample windows with 448-sample overlap and identical color limits. Waveforms are displayed at every twentieth sample; measurements use all samples.
- Automatic decoding uses three variants: DC-removed raw audio; a fourth-order 900–2600 Hz Butterworth bandpass applied with `sosfiltfilt`; and spectral subtraction of the bandpassed signal. Subtraction uses a 512/384 STFT, a noise estimate of 1.6 times the temporal 15th power percentile, and a minimum spectral amplitude gain of 0.15. Each variant is peak-normalized to 0.95 and converted to int16 WAV.
- `sstv==0.2.0` searches for a header/VIS code with automatic mode detection. No image was returned in 12 attempts. Forced headerless output was not treated as a successful decode.
- A synthetic 320 × 240 color-bar image was encoded as Robot36 at 48 kHz, resampled to 9999 Hz, and successfully decoded as one complete image. This checks software functionality, not the original Pi source audio or RF chain.
- Short recordings use an 8192-sample Welch spectrum. The peak selected within 30–52 kHz lies between 41.7 and 42.3 kHz; stronger components outside that search range may exist.

Additional JSON metrics are descriptive peak-to-local-median ratios, not overall SNR or statistical significance. The `sync_rhythm` search takes the maximum within 6.45–6.85 Hz and does not establish SSTV synchronization. Broad-band Hilbert instantaneous-frequency estimates also require caution.

Run the commands above to verify hashes and reproduce durations, clipping counts, short-recording band peaks, automatic decode counts and the synthetic control in `analiz/ciktilar/review.json`. The additional archived spectral ratios and plots are not regenerated by that command. Original WAV files are not changed.

Receiver-input RF level and deviation were not calibrated. To repeat the experiment, convert an image of your choice (`test.png`) into Robot36 SSTV audio at 48 kHz (`sstv48.wav`), or use a ready-made SSTV test signal with the same mode and sample rate. The recordings were made after circuit modifications carried out at different stages of the project. These modifications are described in the project files. A failed automatic decode is not proof of absent SSTV information or impossibility with every decoder or circuit modification.
