__author__ = 'tr1b2669'

import threading
from messages import *
import time
import util
import Queue

class StateT(util.LogMixin):
    def __init__(self, context):
        util.LogMixin.__init__(self)
        self.context = context
        self.transitions = {RSPERROR.__name__: self,
                            PING.__name__: self}
        self.t0 = -1

    def init_transitions(self):
        pass

    def handle(self):
        if self.t0 is -1:
            self.start_timer()
        self.__handle__()

    def disconnected(self):
        pass

    def __handle__(self):
        assert 0, "run not implemented"

    def next(self):
        key = self.get_transition_key()
        if key in self.transitions:
            next_state = self.transitions[key]
            if type(next_state) is not type(self):
                self.stop_timer()
            return next_state

        else:
            self.context.process_message(RSPERROR())
            return self

    def get_transition_key(self):
        return self.context.message.__class__.__name__

    def time_passed(self):
        if self.t0 is not -1:
            return time.clock() - self.t0
        else:
            return 0

    def start_timer(self):
        self.t0 = time.clock()

    def stop_timer(self):
        self.t0 = -1


class PartneredStates(StateT):
    def __init__(self, context):
        StateT.__init__(self, context)

    def init_transitions(self):
        self.transitions[RSPOPDISCON.__name__] = self.context.states['connected']
        pass

    def disconnected(self):
        if self.context.partner_name:
            self.context.send_message_to_partner(RSPOPDISCON())


class Initial(StateT):
    def init_transitions(self):
        self.transitions[CONNECT.__name__] = self.context.states['connecting']

    def __handle__(self):
        self.logger.info('Initial')


class Connecting(StateT):
    def init_transitions(self):
        self.transitions[RSPOK.__name__] = self.context.states['connected']
        self.transitions[RSPINVALID.__name__] = self.context.states['initial']

    def __handle__(self):
        self.logger.info('Connecting')
        if not self.context.message.body or not self.context.message.body.username:
            message = RSPINVALID()
        else:
            username = self.context.message.body.username
            if not self.context.dispatcher.is_name_available(username):
                message = RSPINVALID()
            else:
                self.context.name = username
                message = RSPOK()

        self.context.process_message(message)


class Connected(StateT):
    def init_transitions(self):
        self.transitions[FINDMATCH.__name__] = self.context.states['finding_match']

    def __handle__(self):
        if self.context.partner_name:
            self.context.partner_name = None
            self.context.board_info = None
        self.logger.info('Connected')

class FindingMatch(StateT):
    def init_transitions(self):
        self.transitions[RSPFIRST.__name__] = self.context.states['moving']
        self.transitions[RSPSECOND.__name__] = self.context.states['wait_for_opponent']
        self.transitions[RSPNOMATCH.__name__] = self.context.states['connected']

    def __handle__(self):
        if self.try_partner_up():
            self.logger.info('Partner Found')
        elif self.time_passed() >= 60:
            self.logger.info('No match')
            message = RSPNOMATCH()
            self.context.process_message(message)
        else:
            self.logger.info('Finding partner')

    def try_partner_up(self):
        partnered = self.context.dispatcher.find_partner(self.context)
        if partnered:
            self.logger.debug('found proxy ' + self.context.partner_name)
            message = RSPFIRST()
            message.body.opponent = self.context.partner_name

            message_to_partner = RSPSECOND()
            message_to_partner.body.opponent = self.context.name
            message_to_partner.body.dice = message.body.dice
            self.context.process_message(message)
            self.context.send_message_to_partner(message_to_partner)
            return True
        return False


class WaitForOpponent(PartneredStates):
    def init_transitions(self):
        PartneredStates.init_transitions(self)
        self.transitions[RSPMOVE.__name__] = self.context.states['revertible_moving']
        self.transitions[RSPWRONGMOVE.__name__] = self.context.states['moving']

    def __handle__(self):

        if self.context.partner_name:
            self.logger.info('Waiting move from ' + self.context.partner_name)


class Moving(PartneredStates):
    def init_transitions(self):
        PartneredStates.init_transitions(self)
        self.transitions[MOVE.__name__] = self.context.states['moved']
        self.transitions[RSPTIMEOUT.__name__] = self.context.states['connected']

    def __handle__(self):

        self.logger.info(self.context.partner_name + ' will wait for Move')
        if self.context.partner_name and self.time_passed() >= 3000:
            self.context.send_message_to_partner(RSPOPDISCON())
            self.context.process_message(RSPTIMEOUT())


class Moved(PartneredStates):
    def init_transitions(self):
        PartneredStates.init_transitions(self)
        self.transitions[RSPDICE.__name__] = self.context.states['wait_for_opponent']

    def __handle__(self):
        self.context.board_info.update_board()
        response_to_partner = RSPMOVE()
        response_to_partner.update_from_move(self.context.message)
        response_to_partner.body.board = self.context.board_info.calculate_setup(self.context.message)
        response = RSPDICE()
        response.randomize()
        response_to_partner.body.dice = response.body.dice
        print'MOVED ' + str(response_to_partner.body.board)
        self.logger.info(response_to_partner.deserialize())
        self.context.process_message(response)
        self.context.send_message_to_partner(response_to_partner)


class RevertibleMoving(PartneredStates):
    def init_transitions(self):
        PartneredStates.init_transitions(self)
        self.transitions[MOVE.__name__] = self.context.states['moved']
        self.transitions[WRONGMOVE.__name__] = self.context.states['reverted']
        self.transitions[RSPTIMEOUT.__name__] = self.context.states['connected']

    def __handle__(self):
        if self.context.partner_name and self.time_passed() >= 3000:
            self.context.send_message_to_partner(RSPOPDISCON())
            self.partner_name = None
            self.context.process_message(RSPTIMEOUT())


class Reverted(PartneredStates):
    def init_transitions(self):
        PartneredStates.init_transitions(self)
        self.transitions[RSPWRONGMOVE.__name__] = self.context.states['wait_for_opponent']

    def __handle__(self):
        message = RSPWRONGMOVE()
        message.body.board = self.context.board_info.revert_board()
        print'REVERTED ' + str(message.body.board)
        self.context.process_message(message)
        self.context.send_message_to_partner(message)

        pass


class ThreadedStateMachine(threading.Thread, util.LogMixin):
    def __init__(self):
        threading.Thread.__init__(self)
        util.LogMixin.__init__(self)
        self.states = {
            'initial': Initial(self),
            'connecting': Connecting(self),
            'connected': Connected(self),
            'finding_match': FindingMatch(self),
            'wait_for_opponent': WaitForOpponent(self),
            'moving': Moving(self),
            'moved': Moved(self),
            'revertible_moving': RevertibleMoving(self),
            'reverted': Reverted(self),
        }
        for key, state in self.states.iteritems():
            state.init_transitions()
        self.currentState = self.states['initial']
        self.currentState.handle()
        self.queue = Queue.Queue()
        self.done = False

    def run(self):
        while not self.done:
            self.internal_run()
            try:
                message = self.queue.get_nowait()
                self.logger.info('Message in the queue ' + str(message))
                self.message_received(message.message)
            except Queue.Empty:
                self.logger.debug('Queue empty')
                # short delay, no tight loops
            time.sleep(1)
            if not self.done:
                self.currentState.handle()

    def internal_run(self):
        pass

    def queue_message(self, message):
        self.queue.put(message)

    def message_received(self, message):
        pass
