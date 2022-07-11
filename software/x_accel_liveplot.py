# from time import sleep
from time import sleep
from  smartbit import Phone
import numpy as np
import matplotlib.pyplot as plt

p = Phone()
plt.axis([0, 50, -10, 10])

for i in range(50):
    y = p.get_x_accelo()
    print(y)
    y = np.double(y)
    plt.scatter(i, y)
    sleep(0.1)
    plt.pause(0.1)

plt.show()