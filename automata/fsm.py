"""
Finite state machine
- input alphabet
- set of states
- initial state
- state transition function
- set of final states

https://en.wikipedia.org/wiki/Finite-state_machine
"""


class State:  # pylint: disable-msg=too-few-public-methods
    """an empty state class"""


class FSM:
    """fsm class"""

    def __init__(self, states, alphabet, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.start_state = start_state
        self.final_states = final_states

    def __len__(self):
        return len(self.states)

    def __contains__(self, state):
        return state in self.states
