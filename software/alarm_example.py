from time import sleep
import smartbit

p = smartbit.Phone()

while True:
    prox_val = float(p.get_proxy())
    print(prox_val)
    for _ in range(3):
        if prox_val == 0.0:
            p.write_text("💩💩💩💩")
            p.vibrate(1000)
            p.toggle_led()
        
    sleep(0.1)
    