"""Automaton class"""
from abc import ABC


# pylint: disable-msg=too-few-public-methods
class State:
    """an empty state class"""


class Automaton(ABC):
    """
    that accepts or rejects strings of symbols and only produces a unique
    computation (or run) of the automaton for each input string.
    dfa
    nfa
    """

    def __init__(self, states, alphabet, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.start_state = start_state
        self.final_states = final_states

    def __len__(self):
        return len(self.states)

    def __contains__(self, state):
        return state in self.states
