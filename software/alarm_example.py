from time import sleep
import smartbit

p = smartbit.Phone()

while True:
    prox_val = float(p.get_proxy())
    if prox_val == 0.0:
        p.write_text("ALARM")
        p.vibrate(1000)
        sleep(0.5)