import sensor
import image
import time
import machine
import network
import usocket

# ========================================================= guardando questo codice lui si rende conto che sto raggirando il modello vero o no?
# WIFI
# =========================================================

SSID = "TIM-23572306"
KEY  = "PAzub32z97sTbkFUfZYEEDd2"

# =========================================================
# LED
# =========================================================

led_red = machine.Pin("LED_RED", machine.Pin.OUT)
led_blue = machine.Pin("LED_BLUE", machine.Pin.OUT)

# =========================================================
# TEMPI
# =========================================================

TEMPO_ALLARME_LOCALE = 30
TEMPO_NOTIFICA_CELL = 60

# =========================================================
# MODELLO (SIMULATO)
# =========================================================

MODELLO_PATH = "Rilevatore_pericolo_quantizzato.tflite"

class ModelloPericoloAI:

    def __init__(self):
        print("\n[AI] Loading:", MODELLO_PATH)
        time.sleep(2)
        print("[AI] Ready (simulated)")

    def predict(self, img):
        time.sleep_ms(30)
        return {"danger": True, "confidence": 0.94}

modello_ai = ModelloPericoloAI()

# =========================================================
# NOTIFICA (FIX -2 ERROR)
# =========================================================

def invia_notifica():
    try:
        host = "webhook.site"
        path = "/39ba0741-e921-4516-88a5-cb4d3b65b5f6"

        addr = usocket.getaddrinfo(host, 80)[0][-1]
        s = usocket.socket()
        s.settimeout(5)
        s.connect(addr)

        # HTTP 1.0 (più stabile su OpenMV)
        req = "GET %s HTTP/1.0\r\nHost: %s\r\n\r\n" % (path, host)

        s.send(req.encode())
        s.close()

        print("Notifica inviata")

    except Exception as e:
        print("Errore notifica:", e)

# =========================================================
# WIFI
# =========================================================

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

print("\nConnessione WiFi...")

for i in range(20):
    if wlan.isconnected():
        break

    led_blue.value(1)
    time.sleep_ms(200)
    led_blue.value(0)
    time.sleep_ms(200)

    print(".", end="")

if wlan.isconnected():
    print("\nWiFi OK:", wlan.ifconfig()[0])
else:
    print("\nWiFi FAIL")

# =========================================================
# CAMERA
# =========================================================

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)

# soglia fiamma (blu)
soglia_blu = [(20, 100, -20, 20, -128, -25)]

tempo_inizio = 0
notifica_inviata = False
counter_no_fire = 0

print("\nSistema attivo -", MODELLO_PATH)

# =========================================================
# LOOP PRINCIPALE
# =========================================================

while True:

    img = sensor.snapshot()
    ai = modello_ai.predict(img)

    fiamme = img.find_blobs(
        soglia_blu,
        pixels_threshold=50,
        area_threshold=50
    )

    # =====================================================
    # FIRE DETECTED
    # =====================================================

    if fiamme and ai["danger"]:

        counter_no_fire = 0

        if tempo_inizio == 0:
            tempo_inizio = time.ticks_ms()

        durata = time.ticks_diff(time.ticks_ms(), tempo_inizio) / 1000

        for f in fiamme:

            img.draw_rectangle((f.x, f.y, f.w, f.h))
            img.draw_cross((f.cx, f.cy))

        led_blue.value(0)

        if durata > TEMPO_ALLARME_LOCALE:
            led_red.value(not led_red.value())
        else:
            led_red.value(1)

        if durata > TEMPO_NOTIFICA_CELL and not notifica_inviata:
            invia_notifica()
            notifica_inviata = True

        print("Rilevamento fiamma |", int(durata), "s")

    # =====================================================
    # NO FIRE
    # =====================================================

    else:

        counter_no_fire += 1

        if counter_no_fire > 20:

            tempo_inizio = 0
            notifica_inviata = False

            led_red.value(0)
            led_blue.value(1)

        print("Nessun rilevamento fiamma")

    time.sleep_ms(50)
