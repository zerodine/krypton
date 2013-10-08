import Queue

__author__ = "Thomas Spycher, Philipp Spinnler"
__copyright__ = "Copyright 2013, Zerodine GmbH (zerodine.com) "
__credits__ = ["Thomas Spycher", "Philipp Spinnler"]
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Spycher"
__email__ = "me@tspycher.com"
__status__ = "Development"

import logging
import threading
import time
import datetime

from . import GossipTask

class Gossiping(object):

    applicationContext = None
    logger = logging.getLogger("krypton.gossip")

    _cron = [{"month": "*","day": "*", "weekday": "*", "hour": "*", "minutes": "*/1", "task":"recon"}]

    def __init__(self, applicationContext):
        self.applicationContext = applicationContext

    def start(self):
        self._thread_stop = threading.Event()
        t = threading.Thread(target=self._run, args=())
        t.daemon = True
        t.start()
        return t

    def stop(self):
        '''
        Stops the thread running in the background
        '''
        self._thread_stop.set()
        return True

    def _processCron(self):
        d = datetime.datetime.today()
        for c in self._cron:
            runThis = False
            for key, val in c.items():
                if key == "task" or key == "lastrun":
                    continue

                if val == "*":
                    runThis = True
                    continue
                everyN = 0
                if "/" in val:
                    x = val.split("/")
                    val = x[0]
                    everyN = int(x[1])

                if key == "month":
                    if (everyN and d.month % everyN == 0) or (val == d.month):
                        runtThis = True
                        continue
                elif key == "day":
                    if (everyN and d.day % everyN == 0) or (val == d.day):
                        runtThis = True
                        continue
                elif key == "weekday":
                    if (everyN and d.weekday() % everyN == 0) or (val == d.weekday()):
                        runtThis = True
                        continue
                elif key == "hour":
                    if (everyN and d.hour % everyN == 0) or (val == d.hour):
                        runtThis = True
                        continue
                elif key == "minutes":
                    if (everyN and d.minute % everyN == 0) or (val == d.minute):
                        runtThis = True
                        continue

                runThis = False
                break

            if runThis:
                if "lastrun" in c and time.time() - c["lastrun"] <= 59.0:
                    continue
                self.logger.info("Adding Gossip Cron Task %s" % c["task"])
                c["lastrun"] = time.time()
                if "recon" in c["task"]:
                    task = GossipTask(
                        task=GossipTask.TASK_RECON,
                        gossipServers=self.applicationContext.gossipServers,
                    )
                    task.name = "Reconciliation Task"
                    self.applicationContext.queue.put(task)

    def _run(self):
        while True:
            self._processCron()
            try:
                work = self.applicationContext.queue.get(block=False)
            except Queue.Empty:
                time.sleep(1)
                continue

            self.logger.info("Received work from queue \"%s\"" % work.name)
            if work.doWork():
                self.applicationContext.queue.task_done()
            else:
                if work.givingUp:
                    self.logger.warn("Giving up Processing this Gossiping task")
                else:
                    self.applicationContext.queue.put(work)

if __name__ == "__main__":
    g = Gossiping(None)
    g.processCron()