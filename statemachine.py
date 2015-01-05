__author__ = 'tr1b2669'

import threading
from messages import *
import time
import util
import copy
lock = threading.Lock()
printing_lock = threading.Lock()



class State:
    def __init__(self):
        pass

    def handle(self, context):
        assert 0, "run not implemented"

    def next(self, context):
        assert 0, "next not implemented"


class StateT(State, util.LogMixin):
    def __init__(self):
        State.__init__(self)
        util.LogMixin.__init__(self)
        self.transitions = None
        self.t0 = 0

    def next(self, context):
        key = context.message
        real_key = key.__class__.__name__
        if real_key in self.transitions:
            return self.transitions[real_key]
        else:
            # raise "Input not supported for current state"
            # return a generic error state
            context.message = RSPERROR()
            return self

    def send_message_update_state(self, context):
        self.logger.info('updating message ' + context.message.__class__.__name__)
        context.send_message(context.message)
        context.currentState = self.next(context)


class Initial(StateT):
    def handle(self, context):
        self.logger.info('Initial')

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                CONNECT.__name__: context.connecting
            }
        return StateT.next(self, context)


class Connecting(StateT):
    def handle(self, context):
        self.logger.info('Connecting')
        if 'username' not in context.message.body:
            context.message = RSPERROR()
        else:
            username = context.message.body['username']
            for proxy in context.proxies:
                self.logger.info('proxy name ' + proxy.name)
                if proxy.name == username:
                    context.message = RSPINVALID()
                    break
            else:
                context.name = username
                context.message = RSPOK()

        self.send_message_update_state(context)

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                RSPOK.__name__: context.connected,
                RSPINVALID.__name__: context.initial
            }
        return StateT.next(self, context)


class Connected(StateT):
    def handle(self, context):
        self.logger.info('Connected')

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                FINDMATCH.__name__: context.finding_match
            }
        return StateT.next(self, context)


class FindingMatch(StateT):
    def handle(self, context):
        self.logger.debug('trying lock acquire')
        lock.acquire()
        if context.matching_proxy is not None:
            self.logger.debug('Already matched')
            self.t0 = 0
        elif self.t0 == 0:
            self.t0 = time.clock()
        elif time.clock() - self.t0 >= 60:
            self.logger.info('No match')
            self.t0 = 0
            context.message = RSPNOMATCH()
            self.send_message_update_state(context)
        else:
            self.logger.info('Finding Match')
            if self.try_partner_up(context):
                self.t0 = 0

        self.logger.debug('lock released')
        lock.release()

    def try_partner_up(self, context):
        for proxy in context.proxies:
            self.logger.debug('Current proxy ' + proxy.name)
            if proxy.name == context.name:
                continue
            if type(proxy.currentState) is FindingMatch and proxy.matching_proxy is None:
                self.logger.debug('found proxy ' + proxy.name)
                proxy.block = True
                context.matching_proxy = proxy
                proxy.matching_proxy = context
                message = RSPMATCHSTART()
                message.randomize()
                message_proxy = copy.deepcopy(message)
                message_proxy.body.first_player = not message_proxy.body.first_player
                message_proxy.body.is_white = not message_proxy.body.is_white
                context.message = message
                self.send_message_update_state(context)
                proxy.msgQueue.put(message_proxy.deserialize())
                return True
        return False

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                RSPMATCHSTART.__name__: context.matching,
                RSPNOMATCH.__name__: context.connected
               #write other states here
            }
        return StateT.next(self, context)


class WaitForOpponent(StateT):
    def handle(self, context):
        self.logger.info('Waiting move from ' + context.matching_proxy.name)
        # Find client
        if isinstance(context.message, MOVE):
            context.message = RSPMOVE()
            self.next(context)
        pass

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                MOVE.__name__: context.matching
               #write other states here
            }
        return StateT.next(self, context)


class Moving(StateT):
    def handle(self, context):
        self.logger.info(context.name + ' is Moving')
        # Find client
        if isinstance(context.message, MOVE):
            context.message = RSPMOVE()
            self.next(context)
        pass

    def next(self, context):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                MOVE.__name__: context.matching
               #write other states here
            }
        return StateT.next(self, context)


class ThreadedStateMachine(threading.Thread, util.LogMixin):
    def __init__(self):
        threading.Thread.__init__(self)
        util.LogMixin.__init__(self)
        self.initial = Initial()
        self.connecting = Connecting()
        self.connected = Connected()
        self.finding_match = FindingMatch()
        self.wait_for_opponent = WaitForOpponent()
        self.moving = Moving()

        self.currentState = self.initial
        self.currentState.handle(self)
    #
    # # Template method:
    # def run(self):
    #     self.currentState = self.currentState.next()
    #     self.currentState.run()


