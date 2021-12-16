import multiprocessing
import time
import queue
import threading


class TaskMonitor(threading.Thread):

    def __init__(self):
        super(TaskMonitor, self).__init__()
        self.daemon = True
        self.cancelled = False
        self.signalQueue = multiprocessing.Manager().Queue()
        self.pids = []

    def run(self):
        while not self.cancelled:
            try:
                msg = self.signalQueue.get(block=False)
                #print(f"task pid: {msg}")
                self.pids.append(msg)
            except queue.Empty:
                pass
            time.sleep(1)

    def cancel(self):
        self.cancelled = True

        
