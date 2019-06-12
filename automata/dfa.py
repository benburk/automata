"""Deterministic finite automaton"""
from automaton import Automaton


class DFA(Automaton):
    """Deterministic finite automaton"""

    def __init__(self, states, transitions, start_state, final_states):
        super().__init__(states, start_state, final_states)
        self.transitions = transitions

    def complement(self):
        """return a DFA that is the complement of this DFA"""

    def to_png(self):
        """convert this DFA to a PNG representation"""
