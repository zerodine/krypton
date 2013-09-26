import logging
import threading
import time

__author__ = 'thospy'


class Gossiping(object):

    applicationContext = None
    logger = logging.getLogger("krypton.gossip")

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

    def _run(self):
        while True:
            work = self.applicationContext.queue.get()
            self.logger.info("Received work from queue \"%s\"" % work.name)
            if work.doWork():
                self.applicationContext.queue.task_done()
            else:
                if work.givingUp:
                    self.logger.warn("Giving up Processing this Gossiping task")
                else:
                    self.applicationContext.queue.put(work)
            time.sleep(2)