import matplotlib.pyplot as plt
import statistics

file = open("otherfile.txt","r", encoding="utf-8")

ms = []
lines = file.readlines()
for line in lines:
    if line.startswith("Milliseconds"):
        ms += [int(line.split(":")[1].strip())]

file.close()

print(ms)

# plt.scatter(list(range(100)), ms)
# plt.show()

print("mittelwert: %d" % statistics.mean(ms))
print("standardabweichung %d" % statistics.pstdev(ms))

plt.boxplot(ms)
plt.ylabel("reaktionszeit in ms")
plt.show()