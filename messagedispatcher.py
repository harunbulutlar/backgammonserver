__author__ = 'tr1b2669'
import threading
import Queue
import util
from statemachine import FindingMatch
import copy

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
                    # print 'queued message to' + subscriber.name
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
            # print 'Current proxy ' + subscriber.name
            if requesting_partner.name == subscriber.name:
                continue
            if type(subscriber.currentState) is FindingMatch and subscriber.partner_name is None:
                subscriber.partner_name = requesting_partner.name
                requesting_partner.partner_name = subscriber.name
                subscriber.board_info = SharedBoardInfo()
                requesting_partner.board_info = subscriber.board_info
                # print 'requesting partner name ' + requesting_partner.partner_name
                # print ' subscriber partner name ' + subscriber.partner_name
                return True
        return False


class SharedBoardInfo():
    lock = threading.Lock()
    def __init__(self):
        self.previous_board = copy.deepcopy(util.initial_setup)
        self.board = copy.deepcopy(util.initial_setup)

    @util.synchronized(lock)
    def calculate_setup(self, message):
        move = message.body.move
        counter = 0
        while counter < len(move):
            column1 = move[counter]
            if counter + 1 < len(move):
                column2 = move[counter + 1]
                if column2[1][0] < 0:
                    current_color = self.board[column2[1][0]][0]
                    counter += 1
                    self.move(self.board, column2, current_color)
            self.move(self.board, column1)
            counter += 1
        return copy.deepcopy(self.board)

    @util.synchronized(lock)
    def revert_board(self):
        self.board = copy.deepcopy(self.previous_board)
        return copy.deepcopy(self.board)

    @util.synchronized(lock)
    def update_board(self):
        self.previous_board = copy.deepcopy(self.board)

    def move(self, board, column, color = None):
        if not color:
            color = board[column[0][0]][0]
        board[column[0][0]] = self.decrement(board[column[0][0]])
        board[column[1][0]] = self.increment(board[column[1][0]], color)

    def decrement(self, pair):
        pair[1] -= 1
        if pair[1] == 0:
            pair[0] = 'EMPTY'
        return pair

    def increment(self, pair, color):
        pair[1] += 1
        if pair[1] == 0:
            pair[0] = 'EMPTY'
        else:
            pair[0] = color
        return pair