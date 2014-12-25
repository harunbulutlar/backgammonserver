__author__ = 'tr1b2669'

import threading
import states


class ThreadedStateMachine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        # Initialize states
        self.initial = states.Initial(self)
        self.connected = states.Connected(self)

        self.currentState = self.initial
        self.currentState.handle()

    # Template method:
    def run(self):
        self.currentState = self.currentState.next()
        self.currentState.run()


