# ISS SSTV Lab — RF Experiments with a 433 MHz Receiver

[Türkçe](README.md) | **English**

Can a cheap **XY-MK-5V / MX-RM-5V** remote-control receiver receive SSTV images from the ISS? This project documents the experiments behind that question: retuning the receiver, testing AM and FM reception, recording audio with an ESP32, and analyzing signals in Python.

**Status:** AM melody reception was demonstrated; weak audio and tone observations were consistent with FM reception. **No SSTV image was decoded.** The WAV files are local Raspberry Pi tests, not decoded ISS images or verified recordings of the ISS.

<img src="medya/duzenek_genel.jpeg" alt="Experimental setup with 433 MHz receiver, audio amplifier, speaker and adjustment controls" width="540">

**[Download AM video — MP4, approximately 11 seconds](https://github.com/altunsumerve/iss-sstv-superregen/raw/refs/heads/main/medya/am_melodi_demo.mp4)** · [Hardware photos](medya/README.md) · [Recording review](belgeler/kayit_incelemesi.md) · [WAV recordings](kayitlar/README.md)

The video link opens the raw MP4 file. If your browser downloads it, open the downloaded file in a media player. GitHub's file page may not show a video player for this file.

## Goal and setup

The goal was to explore a low-cost receiver for [ARISS](https://www.ariss.org/) SSTV transmissions. Without a radio or RTL-SDR, I started with a superregenerative 433 MHz module designed for AM/OOK.

| Component | Purpose |
|---|---|
| XY-MK-5V / MX-RM-5V | RF receiver retuned using its adjustable coil |
| LM386, 10 kΩ potentiometer and speaker | Listening to recovered audio |
| BC546, 4.7 kΩ and 1 kΩ resistors | ESP32 external-quench experiment |
| Second 10 kΩ potentiometer and series 4.7 kΩ + 1 kΩ | Adjusting the receiver transistor's base bias in the autodyne experiment |
| Coax-fed dipole, 2 × 16 cm | Experimental antenna for approximately 437 MHz |
| ESP32 | ADC sampling and WAV delivery over Wi-Fi; PWM for external-quench experiments |
| Raspberry Pi 3 + [rpitx](https://github.com/F5OEO/rpitx) | AM, FM-tone and Robot36 test signals |
| Python | Spectra, tone-to-background comparisons and attempted SSTV decoding |

For the SSTV test, `test.png` on the Pi was converted with `pysstv` to **Robot36 audio at 48 kHz**, saved as `sstv48.wav`. The approximately 36-second image audio was transmitted as FM at **437.5 MHz** using `testnfm.sh`. To repeat the experiment, convert an image of your choice into SSTV audio in the same way, or use a ready-made Robot36 SSTV test signal at 48 kHz. This tests a Robot36/FM chain; it does not reproduce an ISS link's signal level, Doppler shift or RF conditions.

Wiring and circuit diagrams: [Wiring guide](belgeler/baglantilar.md#english).

## Results

| Experiment | Observation | Outcome |
|---|---|---|
| Retuning and AM | A melody was heard during a 430–439 MHz sweep after coil adjustment; strongest around 434 MHz | AM reception demonstrated |
| FM slope detection | FM melody was inaudible at the center but audible quietly when tuned to either side | Consistent with slope detection |
| Robot36 SSTV | Neither raw nor processed recordings produced an image | No successful decode |
| FM from quench frequency | An initially promising indication did not persist after reducing Pi leakage | No reliable evidence |
| ESP32 external quenching | Audio became louder without improving the chosen tone-to-background metric | No improvement in tested settings |
| Autodyne / continuous oscillation | The audible whistle could not be shown to track the incoming signal | Inconclusive; board failed during this experiment |

### AM and FM observations

The [AM video](https://github.com/altunsumerve/iss-sstv-superregen/raw/refs/heads/main/medya/am_melodi_demo.mp4) shows the speaker-equipped setup and the Pi frequency sweep. Changing melody tones and harmonics are visible in the [microphone-audio spectrum](grafikler/9_am_video_spektrumu.png). This is a demonstration of the AM test, not evidence of FM/SSTV decoding.

| Frequency | AM melody | FM melody |
|---|---|---|
| 434 MHz | Strongest | Not audible |
| 436 / 437.5 / 439 MHz | Audible | Quietly audible |

For one FM-tone recording, the existing analysis script reported the following around 2304 Hz:

```text
2304 Hz  verici kapali:  +2.0 dB   verici acik:  +5.8 dB
```

`verici kapali` means transmitter off; `verici acik` means transmitter on. This metric compares a narrow frequency region to its surrounding spectral background. It is not the overall audio SNR or receiver sensitivity in dBm. Direct RF leakage must be assessed separately using control recordings.

### Re-examination of the SSTV recordings

Four 60-second recordings were passed through automatic decoding as raw audio, after a 900–2600 Hz bandpass filter, and after spectral subtraction. **None of the 12 attempts produced an image.** The same decoder successfully decoded a separately generated clean Robot36 control signal at the recordings' sample rate of 9999 samples/s. That control image is not an RF reception result.

| Original filename | Samples at full-scale limits | Observation |
|---|---:|---|
| `sstv_1dk (3).wav` | 0% | Quieter recording; no automatic decode |
| `sstv_1dk (4).wav` | 0.1073% | Frequent impulses; no automatic decode |
| `sstv_1dk (5).wav` | 0.1007% | Varying noise and impulses; no automatic decode |
| `sstv_1dk (6).wav` | 0.3615% | Strong impulses especially around 18–32 s and near the end; no automatic decode |

![Spectrogram and waveform comparison of four SSTV tests using identical scales](grafikler/7_sstv_kayit_karsilastirma.png)

Horizontal guides mark 1200, 1500 and 2300 Hz; they are not signal detections. Failure to decode does not prove the recordings contain no SSTV information. A complete, consistent SSTV structure was not verified.

**Clipping:** the firmware's long-recording path multiplies audio by `sesKazanc = 4` by default and clamps it to 16-bit limits. Clipping in the file alone does not establish overload of the RF stage or ADC. A WAV header also cannot prove that no samples were lost during acquisition; device overflow counters are needed for that.

### Quench and autodyne experiments

*Quenching* repeatedly starts and stops oscillation in a superregenerative circuit. [Neal Brown's patent](https://patents.google.com/patent/US3337807A/en) is one source for recovering modulation from the quench signal; it does not guarantee this board will do so.

A component around 42 kHz was examined in short recordings sampled at approximately 200 kHz. In an early experiment, Pi leakage in the 52–60 kHz region produced a misleading indication. The seven most recently reviewed short recordings last approximately **0.145 seconds** each. Reliable recovery of the 2304 Hz test tone from quench-frequency variations was not demonstrated. [Short-recording comparison](grafikler/8_kisa_kayit_karsilastirma.png).

For external quenching, ESP32 GPIO25 drove a BC546 and resistors to pull the receiver transistor's base down periodically. Frequencies of 40–100 kHz and off-time fractions of 10–30% were tested. At the selected 100 kHz / 30% setting, the tone-present metric remained **+5.8 dB**, the same as with external quenching disabled. This result applies only to the tested circuit and settings.

![External-quench wiring using the ESP32 and BC546](grafikler/sema_dis_sondurme.png)

**Second potentiometer:** A separate **10 kΩ potentiometer**, distinct from the audio volume control, was used for the autodyne experiment. Its outer terminals connected to 5 V and GND; its wiper connected to the receiver transistor's base through **4.7 kΩ + 1 kΩ in series**. The end of the 1 kΩ resistor previously connected to the BC546 collector was disconnected first. This was an alternative to PWM quenching, not a simultaneous connection of both circuits to the base. [Detailed wiring and limitations](belgeler/baglantilar.md#english).

![Second 10 kΩ potentiometer used in the autodyne experiment](grafikler/sema_otodin.png)

The diagrams document experimental connections. The autodyne diagram's reference to continuous oscillation describes the intended behavior, not a verified result. Its approximately 0.75 mA estimate applies only to the added resistor branch with an assumed 0.7 V base voltage; it is not the transistor's total current or a guarantee of safe operation. English translations of the diagram labels are in the circuit notes.

The autodyne experiment attempted to obtain a beat signal by running the oscillator continuously. No spectral line tracked a 1 kHz change in the Pi frequency. A line at 3994 Hz was present with the Pi off as well. The board failed before a higher-rate recording could be taken.

## What this experiment establishes — and its limits

- Local AM reception and observations consistent with FM reception are documented; successful ISS SSTV reception is not.
- Broad receiver bandwidth and inefficient FM conversion are possible limitations. Noise, leakage and clipping in the recording chain may also contribute.
- The earlier **20–25 dB below-noise** calculation extrapolated a narrow FFT-region measurement to a wider bandwidth. It is an estimate, not calibrated receiver sensitivity or a definite SSTV decoding threshold.
- Placing the Pi near the receiver does not define a calibrated input level; direct coupling and overdrive can affect the test.
- The recordings were made after circuit modifications carried out at different stages of the project. These modifications are described in the project files.
- Later ideas such as adding an auxiliary RF oscillator have not been validated in this project.

## Setup and analysis

### ESP32

The project used the Arduino IDE and Arduino-ESP32 core 3.x. Fill in the `WIFI_ADI` and `WIFI_SIFRE` placeholders locally in the [firmware](firmware/esp_kayit/esp_kayit.ino), then upload it to the board. Open the address printed in the serial monitor at 115200 baud. Keep real Wi-Fi credentials out of shared files and commits.

### Python

To repeat the latest review, performed with Python 3.12:

```sh
python -m pip install -r requirements.txt
python analiz/ton_olc.py kayitlar/fm_ton_dis_sondurme_kapali.wav --gecis 20
python analiz/sondurme_fm.py kayitlar/h1_pi_kapali_200k_06.wav kayitlar/h3_fm_ton_200k_06.wav
python araclar/fm_temizle.py kayitlar/sstv_fm_deneme.wav
python analiz/kayit_incele.py
```

The final command checks the recordings listed in `kayitlar/index.json` and writes measurements, decoding results and a synthetic positive control to `analiz/ciktilar/`. These generated outputs are ignored by Git. [Review method and limitations](belgeler/kayit_incelemesi.md).

To regenerate the circuit diagrams, run `python -m pip install -r requirements-diagrams.txt`, then `python analiz/semalar.py` from the repository root. `python analiz/grafikler.py` rewrites the first six experiment plots; their interpretation limits are documented in the [plot catalog](grafikler/README.md).

Script options retain their Turkish names: `--gurultu START END` selects a noise-only interval, `--gurultu-dosyasi FILE` supplies a separate noise recording, `--cikti DIRECTORY` sets the output directory, `--gecis SECONDS` sets the transmitter-on time, and `--ton HZ` selects the test tone.

## Files

| Path | Contents |
|---|---|
| [firmware/esp_kayit/](firmware/esp_kayit/) | ESP32 recording server |
| [analiz/](analiz/) | Tone, quench and recording-review scripts |
| [araclar/fm_temizle.py](araclar/fm_temizle.py) | Filtering and attempted SSTV decoding |
| [kayitlar/](kayitlar/README.md) | Raw WAV files, original-name mapping and SHA-256 hashes |
| [medya/](medya/README.md) | Hardware photos and AM demonstration video |
| [grafikler/](grafikler/README.md) | Experiment plots and latest comparisons |
| [belgeler/](belgeler/) | Wiring, review method and numerical results |

## RF testing note

The short jumper used in testing still radiates RF. Account for rpitx harmonics and unwanted coupling; conduct RF tests with appropriate filtering, attenuation and compliance with local rules. Receiving signals from the ISS does not require transmitting.

## License

[MIT](LICENSE)
