# Deney kayıtları / Experiment recordings

[Türkçe](../README.md) · [English](../README.en.md)

Bu dosyalar Pi ile yapılan yerel deneylerdir. ISS kaydı değildir. Ham WAV içeriği korunmuştur. Yeni incelenen 11 dosyanın özgün adları, örnekleme hızları ve SHA-256 özetleri [index.json](index.json) içindedir. Üç dosya mevcut kayıtlarla birebir aynı olduğundan yeniden kopyalanmadı.

These are local Raspberry Pi experiments, not ISS recordings. Raw WAV contents are preserved. [index.json](index.json) records original names, sample rates and SHA-256 hashes for the 11 recently reviewed files. Three were identical to existing recordings and were not duplicated.

## Son inceleme / Latest review

| Özgün ad / Original name | Repo dosyası / Repository file | İçerik / Contents |
|---|---|---|
| `sstv_1dk (3).wav` | [sstv_fm_deneme.wav](sstv_fm_deneme.wav) | Robot36 test, 9999 Hz, 60 s |
| `sstv_1dk (4).wav` | [sstv_fm_deneme_04.wav](sstv_fm_deneme_04.wav) | Robot36 test, 9999 Hz, 60 s |
| `sstv_1dk (5).wav` | [sstv_fm_deneme_05.wav](sstv_fm_deneme_05.wav) | Robot36 test, 9999 Hz, 60 s |
| `sstv_1dk (6).wav` | [sstv_fm_deneme_06.wav](sstv_fm_deneme_06.wav) | Robot36 test, 9999 Hz, 60 s |
| `h1_pi_kapali (6).wav` | [h1_pi_kapali_200k_06.wav](h1_pi_kapali_200k_06.wav) | Pi kapalı / Pi off, 199988 Hz, 0.1445 s |
| `h3_fm_ton (3).wav` | [h3_fm_ton_200k.wav](h3_fm_ton_200k.wav) | FM tone, 199988 Hz, 0.1445 s |
| `h3_fm_ton (4).wav` | [h3_fm_ton_200k_04.wav](h3_fm_ton_200k_04.wav) | FM tone, 199988 Hz, 0.1445 s |
| `h3_fm_ton (5).wav` | [h3_fm_ton_200k_b.wav](h3_fm_ton_200k_b.wav) | FM tone, 199988 Hz, 0.1445 s |
| `h3_fm_ton (6).wav` | [h3_fm_ton_200k_06.wav](h3_fm_ton_200k_06.wav) | FM tone, 199988 Hz, 0.1445 s |
| `h3_fm_ton (7).wav` | [h3_fm_ton_200k_07.wav](h3_fm_ton_200k_07.wav) | FM tone, 199988 Hz, 0.1445 s |
| `h3_fm_ton (8).wav` | [h3_fm_ton_200k_08.wav](h3_fm_ton_200k_08.wav) | FM tone, 199988 Hz, 0.1445 s |

Numaralar özgün dosya adlarından korunmuştur. Kayıtlar, devrede farklı zamanlarda yapılan değişikliklerin ardından alınmıştır. Bu değişiklikler proje dosyalarında açıklanmıştır. / Numbers preserve the original filenames. The recordings were made after circuit modifications carried out at different stages of the project. These modifications are described in the project files.

## Önceki deneyler / Earlier experiments

| Dosya / File | Açıklama / Description |
|---|---|
| [fm_ton_dis_sondurme_kapali.wav](fm_ton_dis_sondurme_kapali.wav) | Dış söndürme kapalı; yaklaşık 20 s sonra FM ton / External quench off; FM tone after approximately 20 s |
| [fm_ton_dis_sondurme_100k_30.wav](fm_ton_dis_sondurme_100k_30.wav) | Dış söndürme 100 kHz, %30 / External quench 100 kHz, 30% |
| [h1_pi_kapali_200k.wav](h1_pi_kapali_200k.wav) | Önceki Pi kapalı kontrolü / Earlier transmitter-off control |
| [h3_fm_ton_200k_sizintili.wav](h3_fm_ton_200k_sizintili.wav) | Sızıntı içeren örnek / Example affected by leakage |
| [otodin_islik_test.wav](otodin_islik_test.wav) | 0–20 s Pi off; 20–40 s 437.500 MHz; 40–60 s 437.501 MHz |

Bu klasör alıcının kaydettiği dosyaları içerir. Deneyi tekrarlamak için kendi seçtiğiniz bir görseli (`test.png`) Robot36 modunda, 48 kHz örnekleme hızında SSTV sesine (`sstv48.wav`) dönüştürebilir veya aynı modda ve örnekleme hızında hazır bir SSTV test sinyali kullanabilirsiniz. / This folder contains receiver recordings. To repeat the experiment, convert an image of your choice (`test.png`) into Robot36 SSTV audio at 48 kHz (`sstv48.wav`), or use a ready-made SSTV test signal with the same mode and sample rate.
