"""Automaton class"""
from abc import ABC


class Automaton(ABC):
    """
    that accepts or rejects strings of symbols and only produces a unique
    computation (or run) of the automaton for each input string.
    """

    def __init__(self, states, start_state, final_states):
        self.alphabet = "ab"
        self.states = states
        self.start_state = start_state
        self.final_states = final_states

    def __len__(self):
        return len(self.states)

    def __contains__(self, state):
        return state in self.states
