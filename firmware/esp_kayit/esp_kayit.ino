// esp_kayit.ino - XY-MK-5V ses cikisini ESP32 ile kaydedip Wi-Fi uzerinden WAV olarak verir.
//
// Baglanti:
//   LM358 pin 1'den gelen telin (pot'un A bacagi) -> 100 nF -> GPIO34
//   GPIO34 -> 100k -> 3V3      GPIO34 -> 100k -> GND      (sinyali ADC'nin ortasina oturtur)
//   ESP32 GND -> kartin GND'si (ortak toprak, sart!)
//
// Kullanim:
//   1. Asagiya Wi-Fi adini ve sifresini yaz, yukle.
//   2. Seri Monitor (115200) IP adresini yazar. Telefondan/bilgisayardan o adrese gir
//      (ya da http://esp-kayit.local).
//   3. Sayfadaki dugmelerle kayit al; tarayici WAV dosyasini indirir.
//
// Arduino IDE: Kart "ESP32 Dev Module", Arduino-ESP32 core 3.x

#include <WiFi.h>
#include <WebServer.h>
#include <ESPmDNS.h>
#include "esp_adc/adc_continuous.h"

// ---- BURAYI DOLDUR ----
const char* WIFI_ADI   = "WIFI_ADINI_YAZ";
const char* WIFI_SIFRE = "WIFI_SIFRENI_YAZ";
// -----------------------

static uint32_t       istenenHiz  = 80000;   // Hz (ADC ornekleme) - sayfadan degistirilebilir
static const size_t   CERCEVE     = 1024;    // bayt (512 ornek)
volatile uint32_t     tasma       = 0;       // ADC tamponu tasma sayaci (kayip veri)
static const uint32_t RAM_ORNEK   = 60000;   // hizli kayit icin en fazla bu kadar ornek (200 kHz'de 0.3 sn)

static bool IRAM_ATTR tasmaGeriCagri(adc_continuous_handle_t, const adc_continuous_evt_data_t*, void*) {
  tasma++;
  return false;
}

WebServer server(80);
adc_continuous_handle_t adc = nullptr;
uint32_t gercekHiz = 80000;            // acilista olculur, WAV basligina yazilir

void adcBaslat() {
  if (adc) {                                 // yeniden kurulum (hiz degisimi)
    adc_continuous_stop(adc);
    adc_continuous_deinit(adc);
    adc = nullptr;
  }
  adc_continuous_handle_cfg_t hc = {};
  hc.max_store_buf_size = CERCEVE * 32;      // ~16k ornek: Wi-Fi takilmalarina tampon
  hc.conv_frame_size = CERCEVE;
  ESP_ERROR_CHECK(adc_continuous_new_handle(&hc, &adc));

  adc_digi_pattern_config_t desen = {};
  desen.atten = ADC_ATTEN_DB_12;
  desen.channel = ADC_CHANNEL_6;             // GPIO34 = ADC1 kanal 6
  desen.unit = ADC_UNIT_1;
  desen.bit_width = SOC_ADC_DIGI_MAX_BITWIDTH;

  adc_continuous_config_t ayar = {};
  ayar.pattern_num = 1;
  ayar.adc_pattern = &desen;
  ayar.sample_freq_hz = istenenHiz;
  ayar.conv_mode = ADC_CONV_SINGLE_UNIT_1;
  ayar.format = ADC_DIGI_OUTPUT_FORMAT_TYPE1;
  ESP_ERROR_CHECK(adc_continuous_config(adc, &ayar));
  adc_continuous_evt_cbs_t cb = {};
  cb.on_pool_ovf = tasmaGeriCagri;
  ESP_ERROR_CHECK(adc_continuous_register_event_callbacks(adc, &cb, nullptr));
  ESP_ERROR_CHECK(adc_continuous_start(adc));
}

// Ham ADC verisini 16 bit isaretli ornege cevirir; kac ornek yazdigini dondurur.
size_t cevir(const uint8_t* ham, uint32_t uzunluk, int16_t* cikis) {
  size_t n = 0;
  for (uint32_t i = 0; i + SOC_ADC_DIGI_RESULT_BYTES <= uzunluk; i += SOC_ADC_DIGI_RESULT_BYTES) {
    const adc_digi_output_data_t* p = (const adc_digi_output_data_t*)&ham[i];
    if (p->type1.channel != ADC_CHANNEL_6) continue;
    int v = (int)p->type1.data - 2048;       // 12 bit -> merkez 0
    cikis[n++] = (int16_t)(v * 16);
  }
  return n;
}

// Gercek ornekleme hizini olc (ESP32'de ADC hizi ayarlanandan biraz farkli cikabiliyor).
void hizOlc() {
  static uint8_t ham[CERCEVE];
  static int16_t tmp[CERCEVE / 2];
  uint32_t ret = 0;
  for (int i = 0; i < 20; i++) adc_continuous_read(adc, ham, CERCEVE, &ret, 100);  // tamponu bosalt
  uint64_t toplam = 0;
  uint32_t t0 = micros();
  while (micros() - t0 < 1000000) {
    if (adc_continuous_read(adc, ham, CERCEVE, &ret, 100) == ESP_OK) toplam += cevir(ham, ret, tmp);
  }
  uint32_t gecen = micros() - t0;
  gercekHiz = (uint32_t)(toplam * 1000000ULL / gecen);
  Serial.printf("Olculen ornekleme hizi: %lu Hz\n", (unsigned long)gercekHiz);
}

void wavBaslik(uint8_t* b, uint32_t ornekSayisi, uint32_t hiz) {
  uint32_t veri = ornekSayisi * 2;
  memcpy(b, "RIFF", 4);
  uint32_t v = 36 + veri;           memcpy(b + 4, &v, 4);
  memcpy(b + 8, "WAVEfmt ", 8);
  v = 16;                           memcpy(b + 16, &v, 4);
  uint16_t s = 1;                   memcpy(b + 20, &s, 2);   // PCM
  s = 1;                            memcpy(b + 22, &s, 2);   // mono
  memcpy(b + 24, &hiz, 4);
  v = hiz * 2;                      memcpy(b + 28, &v, 4);
  s = 2;                            memcpy(b + 32, &s, 2);
  s = 16;                           memcpy(b + 34, &s, 2);
  memcpy(b + 36, "data", 4);
  memcpy(b + 40, &veri, 4);
}

void halkaBirak();
void kayitGonder() {
  if (server.hasArg("hiz")) {
    uint32_t h = constrain(server.arg("hiz").toInt(), 20000, 250000);
    if (h != istenenHiz) {
      istenenHiz = h;
      adcBaslat();
      hizOlc();
    }
  }
  int sn = server.hasArg("sn") ? server.arg("sn").toInt() : 10;
  sn = constrain(sn, 1, 60);
  String ad = server.hasArg("ad") ? server.arg("ad") : "kayit";
  uint32_t toplamOrnek = gercekHiz * (uint32_t)sn;

  static uint8_t ham[CERCEVE];
  static int16_t ornek[CERCEVE / 2];
  uint32_t ret = 0, gonderilen = 0;

  // Yuksek hizda Wi-Fi yetismez: once RAM'e kaydet, sonra gonder (kisa ama kayipsiz).
  if (gercekHiz > 100000) {
    halkaBirak();                              // uzun kayit tamponu varsa birak, RAM'i bu kayda ver
    uint32_t enBuyuk = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    uint32_t sigar = enBuyuk > 24000 ? (enBuyuk - 20000) / 2 : 0;  // Wi-Fi icin pay birak
    uint32_t n = min(toplamOrnek, min((uint32_t)RAM_ORNEK, sigar));
    int16_t* ramTampon = n ? (int16_t*)malloc(n * 2) : nullptr;
    if (!ramTampon) { server.send(500, "text/plain", "RAM yetersiz"); return; }
    for (int i = 0; i < 40; i++) adc_continuous_read(adc, ham, CERCEVE, &ret, 100);
    tasma = 0;
    uint32_t alinan = 0;
    while (alinan < n) {
      if (adc_continuous_read(adc, ham, CERCEVE, &ret, 200) != ESP_OK) continue;
      size_t k = cevir(ham, ret, ornek);
      if (k > n - alinan) k = n - alinan;
      memcpy(&ramTampon[alinan], ornek, k * 2);
      alinan += k;
    }
    uint32_t t = tasma;
    uint8_t b[44];
    wavBaslik(b, n, gercekHiz);
    server.setContentLength(44 + n * 2);
    server.sendHeader("Content-Disposition", "attachment; filename=\"" + ad + ".wav\"");
    server.send(200, "audio/wav", "");
    server.sendContent((const char*)b, 44);
    for (uint32_t i = 0; i < n; i += 2048) {
      uint32_t k = min((uint32_t)2048, n - i);
      server.sendContent((const char*)&ramTampon[i], k * 2);
    }
    free(ramTampon);
    Serial.printf("RAM kaydi gonderildi: %s.wav, %lu ornek (%.2f sn), %lu Hz, tampon tasmasi: %lu\n",
                  ad.c_str(), (unsigned long)n, n / (float)gercekHiz, (unsigned long)gercekHiz, (unsigned long)t);
    return;
  }

  uint8_t baslik[44];
  wavBaslik(baslik, toplamOrnek, gercekHiz);
  server.setContentLength(44 + toplamOrnek * 2);
  server.sendHeader("Content-Disposition", "attachment; filename=\"" + ad + ".wav\"");
  server.send(200, "audio/wav", "");
  server.sendContent((const char*)baslik, 44);

  for (int i = 0; i < 40; i++) adc_continuous_read(adc, ham, CERCEVE, &ret, 100);  // eski veriyi at
  tasma = 0;
  while (gonderilen < toplamOrnek) {
    if (adc_continuous_read(adc, ham, CERCEVE, &ret, 200) != ESP_OK) continue;
    size_t n = cevir(ham, ret, ornek);
    if (n > toplamOrnek - gonderilen) n = toplamOrnek - gonderilen;
    server.sendContent((const char*)ornek, n * 2);
    gonderilen += n;
  }
  Serial.printf("Kayit gonderildi: %s.wav, %d sn, %lu Hz, tampon tasmasi: %lu\n",
                ad.c_str(), sn, (unsigned long)gercekHiz, (unsigned long)tasma);
}


// ---- Uzun ses kaydi (SSTV / ISS gecisi icin) ----
// ADC 20 kHz'de calisir, ikiser ornek ortalanip 10 kHz'e indirilir (SSTV 1.1-2.4 kHz icin bol bol yeter).
// Ayri bir gorev (task) ADC'yi surekli okuyup buyuk bir halka tampona yazar; web tarafi tampondan
// gonderir. Wi-Fi birkaç saniye takilsa bile veri kaybolmaz.
static int16_t*          halka      = nullptr;
static uint32_t          halkaBoy   = 0;
static volatile uint32_t yazIdx     = 0;      // uretici (ADC gorevi) - toplam yazilan ornek
static volatile uint32_t okuIdx     = 0;      // tuketici (web) - toplam okunan ornek
static volatile bool     kayitAktif = false;
static volatile uint32_t halkaTasma = 0;      // tampon dolup atilan ornek sayisi
static volatile int      sesKazanc  = 4;
static TaskHandle_t      adcGorev   = nullptr;

void halkaBirak() {
  if (halka && !kayitAktif) { free(halka); halka = nullptr; halkaBoy = 0; }
}

void adcGorevi(void*) {
  static uint8_t ham[CERCEVE];
  static int16_t ornek[CERCEVE / 2];
  float dc = 0; bool ilk = true; int yarim = 0; bool tek = false;
  for (;;) {
    if (!kayitAktif) { ilk = true; tek = false; vTaskDelay(pdMS_TO_TICKS(20)); continue; }
    uint32_t ret = 0;
    if (adc_continuous_read(adc, ham, CERCEVE, &ret, 100) != ESP_OK) continue;
    size_t n = cevir(ham, ret, ornek);
    for (size_t i = 0; i < n; i++) {
      if (!tek) { yarim = ornek[i]; tek = true; continue; }
      tek = false;
      float v = (yarim + ornek[i]) * 0.5f;
      if (ilk) { dc = v; ilk = false; }
      dc += (v - dc) * 0.0005f;               // yavas DC takibi
      float y = (v - dc) * sesKazanc;
      if (y > 32767) y = 32767;
      if (y < -32768) y = -32768;
      if (yazIdx - okuIdx >= halkaBoy) { halkaTasma++; continue; }   // tampon dolu
      halka[yazIdx % halkaBoy] = (int16_t)y;
      yazIdx = yazIdx + 1;
    }
  }
}

void sesKaydi() {
  if (istenenHiz != 20000) { istenenHiz = 20000; adcBaslat(); hizOlc(); }
  uint32_t dk = server.hasArg("dk") ? server.arg("dk").toInt() : 1;
  dk = constrain(dk, 1, 15);
  sesKazanc = server.hasArg("kazanc") ? constrain(server.arg("kazanc").toInt(), 1, 32) : 4;
  String ad = server.hasArg("ad") ? server.arg("ad") : "ses";
  uint32_t cikisHiz = gercekHiz / 2;
  uint32_t toplam = cikisHiz * 60 * dk;

  if (!halka) {                                // en buyuk bos blogun cogunu tampon yap
    uint32_t enBuyuk = heap_caps_get_largest_free_block(MALLOC_CAP_8BIT);
    halkaBoy = enBuyuk > 60000 ? (enBuyuk - 40000) / 2 : 8192;
    if (halkaBoy > 60000) halkaBoy = 60000;    // 10 kHz'de 6 sn
    halka = (int16_t*)malloc(halkaBoy * 2);
    if (!halka) { server.send(500, "text/plain", "RAM yetersiz"); return; }
    Serial.printf("Halka tampon: %lu ornek (%.1f sn)\n", (unsigned long)halkaBoy, halkaBoy / (float)cikisHiz);
  }
  if (!adcGorev) xTaskCreatePinnedToCore(adcGorevi, "adc", 4096, nullptr, 5, &adcGorev, 1);

  uint8_t baslik[44];
  wavBaslik(baslik, toplam, cikisHiz);
  server.setContentLength(44 + toplam * 2);
  server.sendHeader("Content-Disposition", "attachment; filename=\"" + ad + ".wav\"");
  server.send(200, "audio/wav", "");
  server.sendContent((const char*)baslik, 44);

  static int16_t paket[4096];
  uint32_t ret = 0;
  for (int i = 0; i < 40; i++) adc_continuous_read(adc, (uint8_t*)paket, CERCEVE, &ret, 100);  // eski veriyi at
  tasma = 0; halkaTasma = 0;
  yazIdx = 0; okuIdx = 0;
  kayitAktif = true;

  uint32_t gonderilen = 0, t0 = millis(), sonRapor = millis();
  while (gonderilen < toplam) {
    uint32_t hazir = yazIdx - okuIdx;
    uint32_t k = min(hazir, min((uint32_t)4096, toplam - gonderilen));
    if (k < 1024 && gonderilen + k < toplam) { delay(5); }   // biraz biriksin
    else if (k > 0) {
      for (uint32_t i = 0; i < k; i++) paket[i] = halka[(okuIdx + i) % halkaBoy];
      okuIdx = okuIdx + k;
      server.sendContent((const char*)paket, k * 2);
      gonderilen += k;
    }
    if (!server.client().connected()) { Serial.println("Tarayici baglantiyi kesti, kayit durduruldu."); break; }
    if (millis() - sonRapor > 10000) {
      sonRapor = millis();
      Serial.printf("  kayit: %lu/%lu sn, tampon doluluk %%%lu, kayip: ADC %lu / tampon %lu\n",
                    (unsigned long)(gonderilen / cikisHiz), (unsigned long)(toplam / cikisHiz),
                    (unsigned long)((yazIdx - okuIdx) * 100 / halkaBoy),
                    (unsigned long)tasma, (unsigned long)halkaTasma);
    }
  }
  kayitAktif = false;
  Serial.printf("Ses kaydi bitti: %s.wav, %lu dk, %lu Hz, gercek sure %.1f sn, kayip: ADC %lu / tampon %lu\n",
                ad.c_str(), (unsigned long)dk, (unsigned long)cikisHiz, (millis() - t0) / 1000.0,
                (unsigned long)tasma, (unsigned long)halkaTasma);
}

const char SAYFA[] PROGMEM = R"HTML(<!doctype html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ESP kayit</title>
<style>body{font-family:sans-serif;max-width:480px;margin:24px auto;padding:0 16px}
a{display:block;margin:10px 0;padding:14px;background:#2b6cb0;color:#fff;text-align:center;
border-radius:8px;text-decoration:none;font-size:18px}p{color:#555}</style></head><body>
<h2>XY-MK-5V kayit</h2><p>Ornekleme: %HIZ% Hz. Dugmeye basinca kayit baslar, bitince dosya iner.</p>
<p>GPIO34 ortalama: %VOLT% &nbsp;(sayfayi yenileyince tekrar olculur)</p>
<h3>SSTV / ISS kaydi (10 kHz, uzun, kayipsiz)</h3>
<p>Dugmeye bas, sayfa acik kalsin. Kayit bitince WAV iner. Telefon ekrani kapanmasin.</p>
<a href="/ses?dk=1&ad=sstv_1dk">SSTV testi - 1 dk</a>
<a href="/ses?dk=3&ad=sstv_3dk">SSTV testi - 3 dk</a>
<a href="/ses?dk=12&ad=iss_gecisi">ISS gecisi - 12 dk</a>
<h3>Teshis kayitlari</h3>
<a href="/kayit?sn=10&ad=1_pi_kapali">1) Pi kapali - 10 sn</a>
<a href="/kayit?sn=10&ad=2_tasiyici">2) Sadece tasiyici (tune) - 10 sn</a>
<a href="/kayit?sn=10&ad=3_fm_ton">3) FM ton (testnfm ton.wav) - 10 sn</a>
<a href="/kayit?sn=30&ad=uzun">Serbest kayit - 30 sn</a>
<h3>Hizli ornekleme (200 kHz)</h3><p>Sondurme frekansinin gercek yerini gormek icin. 0.3 sn'lik kayipsiz kayit (RAM'e). Ilk basista hiz olculur (+1 sn).</p>
<a href="/kayit?sn=8&hiz=200000&ad=h1_pi_kapali">H1) Pi kapali - 200 kHz</a>
<a href="/kayit?sn=8&hiz=200000&ad=h2_tasiyici">H2) Sadece tasiyici - 200 kHz</a>
<a href="/kayit?sn=8&hiz=200000&ad=h3_fm_ton">H3) FM ton - 200 kHz</a>
<a href="/kayit?sn=1&hiz=80000&ad=sifirla">Normal hiza don (80 kHz)</a>
<h3>Dis sondurme (GPIO25)</h3><p>Su an: <b>%SON%</b></p>
<form action="/sondur" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
Frekans <select name="f"><option>40</option><option selected>60</option><option>80</option><option>100</option><option>120</option></select> kHz
&nbsp;Kapatma <select name="d"><option>10</option><option selected>20</option><option>30</option><option>40</option><option>50</option></select> %
<button style="padding:10px 16px;font-size:16px">Uygula</button></form>
<a href="/sondur?f=0" style="background:#a33">Dis sondurmeyi KAPAT</a></body></html>)HTML";

float pinVoltaji() {                          // GPIO34'un ortalama voltaji (yaklasik)
  static uint8_t ham[CERCEVE];
  static int16_t tmp[CERCEVE / 2];
  uint32_t ret = 0; double top = 0; uint32_t say = 0;
  for (int i = 0; i < 20; i++) adc_continuous_read(adc, ham, CERCEVE, &ret, 100);
  for (int i = 0; i < 20; i++) {
    if (adc_continuous_read(adc, ham, CERCEVE, &ret, 100) != ESP_OK) continue;
    size_t n = cevir(ham, ret, tmp);
    for (size_t j = 0; j < n; j++) { top += tmp[j] / 16 + 2048; say++; }
  }
  return say ? (top / say) / 4095.0 * 3.1 : -1;
}

const int SONDUR_PIN = 25;
uint32_t sonF = 0, sonD = 0;
void sondurAyarla(uint32_t fk, uint32_t d) {   // fk: kHz, d: % (pinin HIGH oldugu, yani osilatorun kapali oldugu sure)
  ledcDetach(SONDUR_PIN);
  pinMode(SONDUR_PIN, OUTPUT); digitalWrite(SONDUR_PIN, LOW);
  sonF = 0; sonD = 0;
  if (fk == 0) return;
  if (fk > 200) fk = 200;
  if (d < 1) d = 1; if (d > 90) d = 90;
  if (!ledcAttach(SONDUR_PIN, fk * 1000, 8)) { Serial.println("PWM kurulamadi"); return; }
  ledcWrite(SONDUR_PIN, d * 256 / 100);
  sonF = fk; sonD = d;
  Serial.printf("Dis sondurme: %lu kHz, kapatma %%%lu\n", (unsigned long)fk, (unsigned long)d);
}
void sondurIstek() {
  uint32_t fk = server.hasArg("f") ? server.arg("f").toInt() : 0;
  uint32_t d = server.hasArg("d") ? server.arg("d").toInt() : 20;
  sondurAyarla(fk, d);
  server.sendHeader("Location", "/");
  server.send(303);
}

void anaSayfa() {
  String s = FPSTR(SAYFA);
  s.replace("%HIZ%", String(gercekHiz));
  s.replace("%SON%", sonF ? String(sonF) + " kHz, kapatma %" + String(sonD) : String("KAPALI (kart kendi kendine sonduruyor)"));
  float v = pinVoltaji();
  String durum = (v > 1.3 && v < 2.0) ? "<b style='color:green'>TAMAM</b>" : "<b style='color:red'>DUZELT (1.3-2.0 V arasi olmali)</b>";
  s.replace("%VOLT%", String(v, 2) + " V " + durum);
  server.send(200, "text/html", s);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_ADI, WIFI_SIFRE);
  Serial.print("Wi-Fi'a baglaniyor");
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }
  Serial.printf("\nBaglandi! Adres: http://%s\n", WiFi.localIP().toString().c_str());
  if (MDNS.begin("esp-kayit")) Serial.println("Ya da: http://esp-kayit.local");

  pinMode(25, OUTPUT); digitalWrite(25, LOW);   // dis sondurme baslangicta kapali
  adcBaslat();
  hizOlc();

  server.on("/", anaSayfa);
  server.on("/kayit", kayitGonder);
  server.on("/ses", sesKaydi);
  server.on("/sondur", sondurIstek);
  server.begin();
}

void loop() {
  server.handleClient();
}
