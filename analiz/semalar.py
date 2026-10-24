#!/usr/bin/env python3
"""semalar.py - Dis sondurme ve otodin devre semalarini cizer (pip install schemdraw)."""
import schemdraw
import schemdraw.elements as elm

# 1) Dis sondurme: ESP32 GPIO25 -> 4.7k -> BC546 -> 1k -> 2SC3356 bazi
with schemdraw.Drawing(file="grafikler/sema_dis_sondurme.png", dpi=150, show=False) as d:
    d.config(fontsize=11)
    d += elm.Dot(open=True).label("ESP32\nGPIO25 (PWM)", "left")
    d += elm.Resistor().right().label("4.7k")
    q = elm.BjtNpn(circle=True).anchor("base").label("BC546", "right")
    d += q
    d += elm.Ground().at(q.emitter)
    d += elm.Line().up().at(q.collector).length(0.75)
    d += elm.Resistor().up().label("1k", "bottom")
    d += elm.Dot(open=True).label("XY-MK-5V transistörü\n(2SC3356, 'R25') BAZ bacağı", "right")
    d += elm.Label().at((0, -2.4)).label(
        "GPIO25 HIGH → BC546 iletimde → osilatörün bazı toprağa çekilir → osilatör susar\n"
        "Frekans (40–120 kHz) ve kapatma oranı (%10–50) ESP sayfasından seçilir", fontsize=9, halign="left")

# 2) Otodin denemesi: ikinci pot ile baza ayarlanabilir gerilim
with schemdraw.Drawing(file="grafikler/sema_otodin.png", dpi=150, show=False) as d:
    d.config(fontsize=11)
    d += elm.Dot(open=True).label("5V", "left")
    d += elm.Line().right().length(1)
    d += elm.Line().down().length(0.5)
    p = elm.Potentiometer().down()
    d += p
    d += elm.Line().down().length(0.5)
    d += elm.Ground()
    d += elm.Label().at((p.start[0] - 2.3, p.center[1])).label("10k pot\n(ikinci pot)")
    d += elm.Resistor().right().at(p.tap).label("4.7k")
    d += elm.Resistor().right().label("1k")
    d += elm.Dot(open=True).label("2SC3356\nBAZ bacağı", "right")
    d += elm.Label().at((0, -6.4)).label(
        "Bazdaki gerilim değişince osilatör: süperrejeneratif → sürekli salınım (otodin)\n"
        "Taban akımı en fazla ~(5-0.7)/5.7k ≈ 0.75 mA ile sınırlı", fontsize=9, halign="left")
print("ok")
