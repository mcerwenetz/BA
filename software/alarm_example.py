from time import sleep
import smartbit

p = smartbit.Phone()

while True:
    prox_val = float(p.get_proxy())
    print(prox_val)
    if prox_val == 0.0:
        p.write_text("ALARM")
        p.vibrate(1000)
        p.toggle_led()
        
    sleep(0.1)
    