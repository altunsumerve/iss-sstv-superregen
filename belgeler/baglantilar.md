# Bağlantı rehberi / Wiring guide

[Türkçe](#turkce) · [English](#english) · [Türkçe ana sayfa](../README.md) · [English overview](../README.en.md)

<a id="turkce"></a>

## Türkçe

Bu rehber alıcı, ses yükselteci, anten, ESP32 kayıt girişi, dış söndürme ve ikinci potla otodin bağlantılarını içerir.

## Alıcı + ses yükselteci

```
XY-MK-5V                     LM386 (DIP-8)
  VCC ── 5V (ferrit boncuktan geçirerek)
  GND ── GND
  LM358 pin 1 ── 100 nF ── pot A
                           pot C ── GND
                           pot B ── LM386 pin 3
                                   LM386 pin 2, 4 ── GND
                                   LM386 pin 6 ── 5V (+100 µF GND'ye)
                                   LM386 pin 1–8 arası 10 µF (kazanç 200)
                                   LM386 pin 5 ── 220 µF (+) ── hoparlör ── GND
  ANT (bobinin yanındaki etiketsiz delik) ── koaks iç iletken ── dipol kolu 1 (16 cm)
  GND ── koaks örgü ── dipol kolu 2 (16 cm)
```

Not: Modülün üzerindeki yaylı bakır bobin **devrenin parçasıdır**, sökülmez. Anten, bobinin yanındaki, kart kenarındaki etiketsiz deliğe bağlanır.

## ESP32 kayıt girişi

```
ses potunun A bacağı ── 100 nF ── GPIO34
GPIO34 ── 51k ── 3V3
GPIO34 ── 51k ── GND
ESP32 GND ── kart GND
```

GPIO34 ~1.35–1.65 V'ta durmalı. ESP sayfası bu değeri gösterir ("TAMAM" yeşil).

**İpuçları:**
- ESP32'yi alıcıyla **aynı powerbank'ten besleme.** Wi-Fi akım darbeleri hoparlörde bip olarak duyulur.
- Pi'yi ve jumper kablosunu ESP32 kablolarından **en az 1 m** uzak tut. Yoksa Pi'nin sinyali ESP girişine doğrudan kaçar.
- Brownout (yeniden başlama döngüsü) görürsen ESP VIN–GND arasına 470 µF ekle ya da daha güçlü bir USB kaynağı kullan.

## Dış söndürme (deney, iyileşme sağlamadı)

```
Kart transistörü (2SC3356, "R25") baz bacağı ── 1k ── BC546 C
                                                BC546 B ── 4.7k ── ESP32 GPIO25
                                                BC546 E ── GND
```

Baz bacağı, diyot modunda kırmızı prob bu bacaktayken yanındaki bacağa ~0.78 V gösteren bacaktır. 1k'yı doğrudan bacağa lehimle ve kabloyu karta sabitle. SMD bacaklar çekilince kolayca kopar.

ESP sayfasının altından frekans (40–120 kHz) ve kapatma oranı (%10–50) seçilir.

ESP32 ve alıcının GND hattı ortaktır. Bu devrede BC546'nın bazı 4,7 kΩ üzerinden PWM ile sürülür; alıcı transistörünün bazına doğrudan GPIO bağlanmaz. Şemadaki C/B/E etiketleri kolektör/baz/emitördür; fiziksel bacak sırasını göstermez.

![Dış söndürme şeması](../grafikler/sema_dis_sondurme.png)

Denenen 40–100 kHz / %10–30 aralığında seçilen 100 kHz / %30 ayarı, ton varken ölçülen +5,8 dB değerini iyileştirmedi. Arayüzün sunduğu bütün ayarlar için sonuç çıkarılamaz.

<a id="ikinci-pot"></a>

## Otodin denemesi: ikinci 10 kΩ pot

Otodin denemesinde kullanılan ikinci pot **10 kΩ** değerindedir. Bu pot LM386'nın ses potundan ayrıdır; alıcı transistörünün baz gerilimini değiştirerek kendi söndürmesini durdurmak ve sürekli osilasyonu denemek için kullanıldı.

```text
5 V ── ikinci 10 kΩ potun dış ucu
GND ── ikinci 10 kΩ potun diğer dış ucu
       potun orta ucu ── 4,7 kΩ ── 1 kΩ ── 2SC3356 baz
```

Dış söndürme devresindeki 1 kΩ direncin BC546 kolektörüne bağlı ucu ayrılarak ikinci potun 4,7 kΩ koluna bağlandı. **Otodin bağlantısında BC546 kolektörü bu baz koluna bağlı değildir.** Ortak GND korunur. İkinci potun görevi ses seviyesini veya PWM frekansını ayarlamak değildir.

![İkinci pot / otodin bağlantısı](../grafikler/sema_otodin.png)

Notlarda, bağlantı öncesinde baz geriliminin ölçülüp potun orta ucunun aynı gerilime ayarlandığı yöntem tarif ediliyor. Ancak bir ıslık duyulması tek başına sürekli osilasyonun veya FM çözümünün doğrulanması değildir. `otodin_islik_test.wav` kaydında Pi 437,500 MHz'den 437,501 MHz'e değiştirildiğinde izleyen bir çizgi görülmedi; 3994 Hz çizgisi Pi kapalıyken de vardı. Kart, 80 kHz kayıt alınamadan bu deneyde çalışmaz hâle geldi. Arızanın kesin nedeni belirlenmedi.

Şemadaki “sürekli salınım” ifadesi amaçlanan davranıştır. `(5 − 0,7) / 5,7 kΩ ≈ 0,75 mA` hesabı, yalnızca ek direnç kolu ve varsayılan baz gerilimi içindir; kartın mevcut kutuplama yolu nedeniyle toplam baz akımını vermez ve güvenli çalışma garantisi değildir. Bu bağlantı, başarılı bir SSTV alıcı tasarımı olarak sunulmaz.

<a id="pi-komutlari"></a>

## Raspberry Pi test vericisi (rpitx)

Kurulum (Raspberry Pi OS Trixie'de `libraspberrypi-dev` paketi yok, userland'ı derlemek gerekiyor):
```
sudo apt install git cmake build-essential libfftw3-dev libsndfile1-dev sox
git clone https://github.com/raspberrypi/userland && cd userland && ./buildme
echo /opt/vc/lib | sudo tee /etc/ld.so.conf.d/00-vmcs.conf && sudo ldconfig
cd ~ && git clone https://github.com/F5OEO/rpitx && cd rpitx && ./install.sh
```

Test sinyalleri (**rpitx sesi 48 kHz'de çalar**):
```
sox -n -r 48000 -b 16 -c 1 ton48.wav synth 10 sine 1000
pip install --break-system-packages pysstv
python3 -m pysstv --mode Robot36 --rate 48000 resim.png sstv48.wav
```

Komutlar:
```
sudo ./tune -f 437500000                         # sadece taşıyıcı
sudo ./testam.sh 436e6 melodi.wav                # AM
sudo ./testnfm.sh 437.5e6 ton48.wav              # dar FM
sudo killall rpitx csdr                          # durdur

# AM frekans taraması
for f in 430 432 434 436 437.5 439 441; do echo "=== $f MHz ==="; sudo timeout 8 ./testam.sh ${f}e6 melodi.wav; sudo killall rpitx csdr 2>/dev/null; sleep 1; done
```

<a id="english"></a>

## English

This guide covers the receiver, audio amplifier, antenna, ESP32 recording input, external quenching and the second potentiometer used in the autodyne experiment.

### Receiver, audio amplifier and antenna

```text
XY-MK-5V                     LM386 (DIP-8)
  VCC ── 5 V through a ferrite bead
  GND ── GND
  LM358 pin 1 ── 100 nF ── volume pot A
                           volume pot C ── GND
                           volume pot B (wiper) ── LM386 pin 3
                                   LM386 pins 2, 4 ── GND
                                   LM386 pin 6 ── 5 V (+100 µF to GND)
                                   LM386 pins 1–8 bridged by 10 µF (gain 200)
                                   LM386 pin 5 ── 220 µF (+) ── speaker ── GND
  ANT (unlabeled hole beside coil) ── coax core ── dipole arm 1 (16 cm)
  GND ── coax braid ── dipole arm 2 (16 cm)
```

The volume potentiometer is 10 kΩ. The spring-shaped copper coil is part of the receiver circuit and stays on the board. Connect the antenna to the unlabeled hole at the board edge beside that coil.

### ESP32 recording input

```text
Volume pot terminal A ── 100 nF ── GPIO34
GPIO34 ── 51 kΩ ── 3V3
GPIO34 ── 51 kΩ ── GND
ESP32 GND ── receiver GND
```

The ESP32 page displays the GPIO34 bias voltage; the documented target range is approximately 1.35–1.65 V.

- Separate receiver and ESP32 power supplies reduced audible interference from Wi-Fi current bursts in the experiments.
- Keep the Pi and its jumper at least 1 m from the ESP32 wiring when checking for direct test-signal leakage.
- The connection notes suggest 470 µF across ESP32 VIN–GND or a stronger USB supply if brownout resets occur.

### ESP32 external quenching

```text
ESP32 GPIO25 ── 4.7 kΩ ── BC546 base (B)
                         BC546 emitter (E) ── GND
                         BC546 collector (C) ── 1 kΩ ── receiver transistor base
ESP32 GND ── receiver GND
```

The receiver transistor is identified in the experiment notes as 2SC3356, marked “R25”. C/B/E identify electrical terminals, not a physical package pin order. GPIO25 drives the BC546 through a resistor, not the receiver base directly.

![External-quench circuit](../grafikler/sema_dis_sondurme.png)

Diagram translation: GPIO25 HIGH drives the BC546 on to pull down the receiver oscillator's base. The ESP32 page offers 40–120 kHz and 10–50% off-time. The experiment tested 40–100 kHz and 10–30%; the selected 100 kHz / 30% setting produced the same +5.8 dB tone-to-background metric as quenching disabled. This does not establish performance across every setting available in the interface.

### Autodyne experiment: second 10 kΩ potentiometer

```text
5 V ── outer terminal of second 10 kΩ potentiometer
GND ── other outer terminal
       wiper ── 4.7 kΩ ── 1 kΩ ── receiver transistor base
```

For this configuration, the end of the 1 kΩ resistor connected to the BC546 collector was disconnected and connected to the potentiometer's 4.7 kΩ branch instead. **The BC546 collector is not connected to this base branch in the autodyne configuration.** Keep the common ground. This control adjusts base bias; it is not the volume or PWM-frequency control.

![Autodyne circuit with second potentiometer](../grafikler/sema_otodin.png)

Diagram labels: “ikinci pot” means second potentiometer; “BAZ bacağı” means base terminal. The intended transition from self-quenching to continuous oscillation was not verified. The diagram's `(5 − 0.7) / 5.7 kΩ ≈ 0.75 mA` estimate concerns the added resistor branch with an assumed base voltage only. It does not include the board's existing bias path, determine total base current, or guarantee safe operation.

The supplied notes describe matching the potentiometer's wiper voltage to the measured base voltage before connecting it. Hearing a whistle alone does not establish continuous oscillation or FM recovery. In `otodin_islik_test.wav`, no line tracked the Pi's change from 437.500 to 437.501 MHz. The 3994 Hz line was also present with the Pi off. The board stopped working during this experiment before an 80 kHz recording could be made; the exact failure cause was not established.

These are records of an inconclusive experiment, not a validated SSTV receiver design.

### Raspberry Pi test transmitter

Use the shared [rpitx setup and test commands](#pi-komutlari) above. The commands cover a carrier, AM melody, FM tone and AM frequency sweep. Generate the audio at **48 kHz**. To test SSTV, convert an image of your choice to Robot36 audio or use a ready-made Robot36 signal at the same sample rate.
