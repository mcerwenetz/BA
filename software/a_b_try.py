import random
from time import sleep
from  smartbit import Phone

p = Phone()
score = 0

for i in range(5):
    correct = random.choice(["A","B"])
    print(correct)
    guess = p.get_button()
    if guess == correct:
        score+=1
        p.write_text("punkte: %d" % score)
    else:
        score=0
        p.write_text("leider falsch. 0 Punkte.")
if score == 5:
    p.write_text("Gewonnen!")
    p.vibrate(1000)

else:
    p.write_text("Leider nicht alles richtig")


sleep(5)
p.write_text("output")

    
