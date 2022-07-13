from matplotlib import pyplot as plt

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 22}

plt.rc('font', **font)

at_uni = [35, 38, 78, 88, 137]
at_home =[130, 160, 170, 190, 240, 225]
vm = [100, 130, 150, 175, 220]
names = ["SWT", "Zuhause (DSL)", "VM Zuhause"]

plt.boxplot([at_uni, at_home, vm])
# plt.xticks(["a","b","c"])
frame = plt.gca()
frame.set_xticklabels(names)
plt.ylabel("RTT rpc [ms]")
plt.show()