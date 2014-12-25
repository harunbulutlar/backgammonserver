__author__ = 'tr1b2669'


class State:
    def __init__(self):
        pass

    def handle(self):
        assert 0, "run not implemented"

    def next(self):
        assert 0, "next not implemented"


class StateT(State):
    def __init__(self, state_context):
        State.__init__(self)
        self.transitions = None
        self.context = state_context

    def next(self):
        key = self.context.message
        if key in self.transitions:
            return self.transitions[key]
        else:
            # raise "Input not supported for current state"
            # return a generic error state
            message = "Generic error message"
            self.context.send(message)
            return self


class Initial(StateT):
    def handle(self):
        print("Waiting for a connection")

    def next(self):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
               #write other states here
            }
        return StateT.next(self)


class Connected(StateT):
    def handle(self):
        self.context.name = self.context.message.name

    def next(self):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
               #write other states here
            }
        return StateT.next(self)