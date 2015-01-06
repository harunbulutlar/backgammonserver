__author__ = 'tr1b2669'
import threading
import Queue
import util
from statemachine import FindingMatch


class Dispatcher():
    lock = threading.Lock()

    def __init__(self):
        self.queue = Queue.Queue()
        self.subscribers = []

    @util.synchronized(lock)
    def register(self, subscriber):
        self.subscribers.append(subscriber)

    @util.synchronized(lock)
    def unregister(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    @util.synchronized(lock)
    def dispatch(self):
        self.subscribers = [t for t in self.subscribers if not t.done]
        try:
            message = self.queue.get_nowait()
            for subscriber in self.subscribers:
                if subscriber.name == message.receiver_name:
                    print 'queued message to' + subscriber.name
                    subscriber.queue_message(message)
        except Queue.Empty:
            pass
            # print 'dispatcher queue is empty'

    @util.synchronized(lock)
    def is_name_available(self, name):
        for subscriber in self.subscribers:
            if subscriber.name == name:
                return False
        return True


    @util.synchronized(lock)
    def queue_message(self, message):
        self.queue.put(message)

    @util.synchronized(lock)
    def find_partner(self, requesting_partner):
        if requesting_partner.partner_name:
            return False
        for subscriber in self.subscribers:
            print 'Current proxy ' + subscriber.name
            if requesting_partner.name == subscriber.name:
                continue
            if type(subscriber.currentState) is FindingMatch and subscriber.partner_name is None:
                subscriber.partner_name = requesting_partner.name
                requesting_partner.partner_name = subscriber.name
                print 'requesting partner name ' + requesting_partner.partner_name
                print ' subscriber partner name ' + subscriber.partner_name
                return True
        return False


