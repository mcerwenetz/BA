# from time import sleep
from time import sleep
from  smartbit import Phone
import numpy as np
import matplotlib.pyplot as plt

p = Phone()
SLEEP=0.0005
RANGE = 500
plt.axis([0, RANGE, -10, 10])

for i in range(RANGE):
    y = p.get_x_accelo()
    print(y)
    y = np.double(y)
    plt.plot(i, y, "-o")
    sleep(SLEEP)
    plt.pause(SLEEP)

plt.show()