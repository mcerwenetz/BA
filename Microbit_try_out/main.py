from microbit import *
import random

TIME = 500
rand_mode = True

def flash(time):
    display.show(Image.HEART)
    sleep(time / 2)
    display.show(" ")
    sleep(time / 2)


while True:
    if rand_mode == False:
        flash(TIME)
    else:
        flash(random.randint(0, 400))
    if button_a.is_pressed():
        rand_mode = not rand_mode

