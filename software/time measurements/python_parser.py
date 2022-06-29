import matplotlib.pyplot as plt
import statistics

file = open("mes.txt","r", encoding="utf-8")

ms = []
lines = file.readlines()
for line in lines:
    if line.startswith("real"):
        line = line.split("\t")[1].split("m")[1].replace(",",".")[:-2]
        
        ms += [int(float(line)*1000)]

file.close()

# print(ms)

# plt.scatter(list(range(100)), ms)
# plt.show()

print("mittelwert: %d" % statistics.mean(ms))
print("standardabweichung %d" % statistics.pstdev(ms))

plt.boxplot(ms)
plt.ylabel("RTT rpc [ms]")
frame = plt.gca()
frame.get_xaxis().set_visible(False)
plt.show()
