# Untitled - By: federica - Mon May 11 2026


import csi, machine, time, os

# 1. RESET FISICO DEL SENSORE
print("Reset hardware del sensore...")
cam = csi.CSI()
cam.reset()
cam.pixformat(csi.RGB565)
cam.framesize(csi.QVGA)
time.sleep(2)

# Messaggio aggiornato per condizione di NON PERICOLO
print("Inizio acquisizione dataset: CONDIZIONE DI SICUREZZA (NO PERICOLO)...")

for i in range(50):
    try:
        # Scatto veloce
        img = cam.snapshot()

        # NOME FILE MODIFICATO: Identifica la condizione di sicurezza/non pericolo
        nome = "sicurezza_no_pericolo_%d.jpg" % i

        # SCRITTURA SULLA MEMORIA FLASH
        with open(nome, "wb") as f:
            f.write(img.compress(quality=35))

        # Salvataggio immediato
        os.sync()

        print("Scatto SICUREZZA %d salvato" % i)

        # LED Blu per confermare il successo
        machine.Pin("LED_BLUE", machine.Pin.OUT).on()
        time.sleep_ms(100)
        machine.Pin("LED_BLUE", machine.Pin.OUT).off()

        # Aspetta 2 secondi per non affaticare la memoria
        time.sleep(2)

    except Exception as e:
        print("Errore critico al frame %d: %s" % (i, e))
        if "ENODEV" in str(e):
            cam.reset()
            time.sleep(1)
        continue

print("Sessione terminata. Dataset NON PERICOLO pronto per il trasferimento.")
