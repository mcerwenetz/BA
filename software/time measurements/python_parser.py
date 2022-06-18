import matplotlib.pyplot as plt
import statistics

file = open("mes.txt","r", encoding="utf-8")

ms = []
lines = file.readlines()
for line in lines:
    ms += [int(line)*1000]

file.close()

print(ms)

# plt.scatter(list(range(100)), ms)
# plt.show()

#print("mittelwert: %d" % statistics.mean(ms))
#print("standardabweichung %d" % statistics.pstdev(ms))

#plt.boxplot(ms)
#plt.ylabel("reaktionszeit in ms")
#plt.show()
