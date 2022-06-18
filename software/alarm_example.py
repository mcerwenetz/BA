from time import sleep
import smartbit

p = smartbit.Phone()

while True:
    prox_val = float(p.get_proxy())
    if prox_val == 0.0:
        p.write_text("ALARM")
        for _ in range(5):
            p.vibrate(1000)
            p.toggle_led()
            sleep(0.2)
    sleep(0.5)
    