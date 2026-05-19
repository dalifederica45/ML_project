# Untitled - By: federica - Mon May 11 2026

import csi, machine, time, os

# 1. RESET FISICO DEL SENSORE
print("Reset hardware del sensore...")
cam = csi.CSI()
cam.reset()
cam.pixformat(csi.RGB565)
cam.framesize(csi.QVGA)
time.sleep(2)

# Messaggio aggiornato per identificare il dataset di PERICOLO
print("Inizio acquisizione dataset: CONDIZIONE DI PERICOLO (FUOCO/EMERGENZA)...")

for i in range(50):
    try:
        # Scatto veloce
        img = cam.snapshot()

        # NOME FILE MODIFICATO: aggiunto prefisso 'pericolo' per evitare sovrascritture
        nome = "pericolo_%d.jpg" % i

        # PROVA DI SCRITTURA FORZATA
        with open(nome, "wb") as f:
            f.write(img.compress(quality=35))

        # Diciamo al sistema di salvare IMMEDIATAMENTE
        os.sync()

        print("Scatto PERICOLO %d salvato correttamente" % i)

        # LED Rosso per indicare il pericolo (se disponibile sulla tua scheda)
        # Se non hai il LED rosso, usa quello Blu come nel codice originale
        try:
            machine.Pin("LED_RED", machine.Pin.OUT).on()
            time.sleep_ms(100)
            machine.Pin("LED_RED", machine.Pin.OUT).off()
        except:
            machine.Pin("LED_BLUE", machine.Pin.OUT).on()
            time.sleep_ms(100)
            machine.Pin("LED_BLUE", machine.Pin.OUT).off()

        # Aspetta 2 secondi per permettere alla flash di scrivere senza errori
        time.sleep(2)

    except Exception as e:
        print("Errore critico al frame %d: %s" % (i, e))
        # Se ricevi ENODEV, resettiamo la cam nel loop
        if "ENODEV" in str(e):
            cam.reset()
            time.sleep(1)
        continue

print("Sessione PERICOLO terminata. Verifica i file sulla memoria.")
