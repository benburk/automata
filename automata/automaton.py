"""Automaton class"""


class Automaton:
    """
    that accepts or rejects strings of symbols and only produces a unique
    computation (or run) of the automaton for each input string.
    """

    def __init__(self):
        raise NotImplementedError

    def accepts_input(self, str):
        """Return True if this automaton accepts the given input."""

