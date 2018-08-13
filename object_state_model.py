#! /usb/lib/env python
import time

# https://dev.to/karn/building-a-simple-state-machine-in-python

class AbstractState(object):
    var = 33
    def __init__(self):
        print 'Processing current state:', str(self)
    def do_State(self):
        raise NotImplementedError()
    def new_Command(self):
        raise NotImplementedError()
    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()
    def __str__(self):
        """
        Returns the name of the State.
        """
        return self.__class__.__name__

class INIT(AbstractState):
    def do_State(self):
        time.sleep(1)
        self.var = 355
        return IDLE()
    def new_Command(self, command):
        print command
        print "new_com_in_INIT"

class IDLE(AbstractState):
    def do_State(self):
        print "do_IDLE"
        self.var = 35
        self.new_Command()
        return IDLE()
    def new_Command(self, command):
        print command
        print self.var
        return IDLE()

class Autocopter(object):
    def __init__(self):
        self.state = INIT()
        self.state = self.state.do_State()
    def new_command(self, command):
        self.state = self.state.new_Command(command)

st = Autocopter()
st.state
st.new_command("wefaf")
st.new_command("412423")
st.new_command("fsdgfbwertbteb")
st.new_command("1451252")