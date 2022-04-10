import threading
import queue
import time

class Record:
    def __init__(self, fun, arg) -> None:
        self.fun=fun
        self.arg=arg


class WorkerThread(threading.Thread):
    def __init__(self, workinQueue : queue.Queue):
        super().__init__()
        self.workinQueue = workinQueue

    def run(self) -> None:
        while True:
            record = self.workinQueue.get()
            record.fun(record.arg)
            print("Hello from Worker")
            time.sleep(3)


class ProdThread(threading.Thread):
    def __init__(self, workinQueue : queue.Queue, arg : str):
        super().__init__()
        self.workinQueue = workinQueue
        self.arg = arg

    def run(self) -> None:
        while True:
            record = Record(functi, self.arg)
            workinQueue.put(record)
            time.sleep(2)
            

def functi(i : str):
    print(f"Hallo {i}")

workinQueue = queue.Queue()
wt = WorkerThread(workinQueue)
pt1 = ProdThread(workinQueue, "1")
pt2 = ProdThread(workinQueue, "2")

wt.start()
pt1.start()
pt2.start()

wt.join()
pt1.join()
pt2.join()
