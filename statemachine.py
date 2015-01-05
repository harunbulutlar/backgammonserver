__author__ = 'tr1b2669'

import threading
from messages import *
import time
import util
import copy

lock = threading.Lock()


class StateT(util.LogMixin):
    def __init__(self, context):
        util.LogMixin.__init__(self)
        self.context = context
        self.transitions = {RSPERROR.__name__: self}
        self.t0 = -1

    def init_transitions(self):
        pass

    def handle(self):
        if self.t0 is -1:
            self.start_timer()
        self.__handle__()

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
        if not self.context.message.body.username:
            message = RSPERROR()
        else:
            username = self.context.message.body.username
            for proxy in self.context.proxies:
                self.logger.info('proxy name ' + proxy.name)
                if proxy.name == username:
                    message = RSPINVALID()
                    break
            else:
                self.context.name = username
                message = RSPOK()

        self.context.process_message(message)


class Connected(StateT):
    def init_transitions(self):
        self.transitions[FINDMATCH.__name__] = self.context.states['finding_match']

    def __handle__(self):
        self.logger.info('Connected')


class FindingMatch(StateT):
    def init_transitions(self):
        self.transitions[RSPMATCHSTART.__name__ + 'first'] = self.context.states['moving']
        self.transitions[RSPMATCHSTART.__name__] = self.context.states['wait_for_opponent']
        self.transitions[RSPNOMATCH.__name__] = self.context.states['connected']

    def __handle__(self):
        self.logger.debug('trying lock acquire')
        lock.acquire()
        if self.context.matching_proxy is not None:
            self.logger.debug('Already matched')
        elif self.time_passed() >= 60:
            self.logger.info('No match')
            message = RSPNOMATCH()
            self.context.process_message(message)
        else:
            self.logger.info('Finding Match')
            self.try_partner_up()

        self.logger.debug('lock released')
        lock.release()

    def try_partner_up(self):
        for proxy in self.context.proxies:
            self.logger.debug('Current proxy ' + proxy.name)
            if proxy.name == self.context.name:
                continue
            if type(proxy.currentState) is FindingMatch and proxy.matching_proxy is None:
                self.logger.debug('found proxy ' + proxy.name)
                proxy.block = True
                self.context.matching_proxy = proxy
                proxy.matching_proxy = self.context
                message = RSPMATCHSTART()
                message.randomize()

                message_proxy = copy.deepcopy(message)
                message_proxy.body.first_player = not message_proxy.body.first_player
                message_proxy.body.is_white = not message_proxy.body.is_white

                self.context.is_white = message.body.is_white
                proxy.is_white = message_proxy.body.is_white
                proxy.board = message.body.board
                self.context.board = message.body.board
                self.context.process_message(message)
                proxy.msgQueue.put(message_proxy)
                return True
        return False

    def get_transition_key(self):
        if isinstance(self.context.message, RSPMATCHSTART):
            if self.context.message.body.first_player:
                return RSPMATCHSTART.__name__ + 'first'

        return StateT.get_transition_key(self)


class WaitForOpponent(StateT):
    def init_transitions(self):
        self.transitions[RSPMOVE.__name__] = self.context.states['moving']
        self.transitions[RSPOPDISCON.__name__] = self.context.states['finding_match']

    def __handle__(self):
        if self.context.matching_proxy:
            self.logger.info('Waiting move from ' + self.context.matching_proxy.name)


class Moving(StateT):
    def init_transitions(self, ):
        self.transitions[MOVE.__name__] = self.context.states['moved']
        self.transitions[WRONGMOVE.__name__] = self.context.states['moved']
        self.transitions[RSPTIMEOUT.__name__] = self.context.states['connected']

    def __handle__(self):
        self.logger.info(self.context.name + ' is Moving')
        # Find client

        if self.time_passed() >= 60:
            self.context.matching_proxy.msgQueue.put(RSPOPDISCON())

            self.context.matching_proxy.matching_proxy = None
            self.context.matching_proxy = None
            self.context.process_message(RSPTIMEOUT())


class Moved(StateT):
    def init_transitions(self):
        self.transitions[RSPDICE.__name__] = self.context.states['wait_for_opponent']
        self.transitions[RSPINVALID.__name__] = self.context.states['moving']

    def __handle__(self):
        self.logger.info(self.context.name + ' move made')
        response = RSPMOVE()
        response.update_from_move(self.context.message)
        if isinstance(self.context.message, WRONGMOVE):
            if self.context.wrong_move_flag:
                self.context.process_message(RSPINVALID)
            else:
                self.context.matching_proxy.wrong_move_flag = True
                response.body.board = self.context.board
                response.body.wrong_move = True
                response.body.move = ()
        else:
            self.context.wrong_move_flag = False
            # Find client
            response.body.board = self.calculate_setup(self.context.message)
            self.logger.info(response.deserialize())
            self.context.matching_proxy.board = self.context.board
            dice = RSPDICE()
            dice.body.dice = response.body.dice
            self.context.process_message(dice)
            self.context.matching_proxy.msgQueue.put(response)

    def calculate_setup(self, move_message):
        if self.context.is_white:
            str = 'WHITE'
        else:
            str = 'BLACK'
        move = move_message.body.move
        self.context.board[move[0][0]] = [str,self.context.board[move[0][0]][1]-1]
        self.context.board[move[0][1]] = [str,self.context.board[move[0][1]][1]+1]
        self.context.board[move[1][0]] = [str,self.context.board[move[1][0]][1]-1]
        self.context.board[move[1][1]] = [str,self.context.board[move[1][1]][1]+1]
        return self.context.board



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
        }
        for key, state in self.states.iteritems():
            state.init_transitions()

        self.currentState = self.states['initial']
        self.currentState.handle()
