"""Deterministic finite automaton"""
from collections import defaultdict

import pydot
from automaton import Automaton
from automaton import State


class DFA(Automaton):
    """Deterministic finite automaton"""

    # pylint: disable-msg=too-many-arguments
    def __init__(self, states, alphabet, transitions, start_state, final_states):
        super().__init__(states, alphabet, start_state, final_states)
        self.transitions = transitions

    @classmethod
    def from_atom(cls, atom, alphabet="ab"):
        """create a DFA from a string"""
        state = start_state = State()
        garbage = State()
        states = {start_state, garbage}
        transitions = {garbage: {symbol: garbage for symbol in alphabet}}

        for char in atom:
            new_state = State()
            transitions[state] = {
                symbol: new_state if char == symbol else garbage for symbol in alphabet
            }
            state = new_state
            states.add(state)

        # have all edges from final state point to garbage state
        transitions[state] = {symbol: garbage for symbol in alphabet}
        return cls(states, alphabet, transitions, start_state, {state})

    def __iter__(self):
        visited = {self.start_state}
        queue = [self.start_state]
        while queue:
            state = queue.pop()
            yield state
            for symbol in self.alphabet:
                neighbour = self.transitions[state][symbol]
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    def complement(self):
        """return the complement of the dfa"""
        lookup = {state: State() for state in self.states}  # create new states
        transitions = {}
        for state, paths in self.transitions.items():
            transitions[lookup[state]] = {
                symbol: lookup[state] for symbol, state in paths.items()
            }
        final_states = {lookup[state] for state in self.states - self.final_states}

        return DFA(
            set(lookup.values()),
            self.alphabet,
            transitions,
            lookup[self.start_state],
            final_states,
        )

    def to_png(self, file_name="out.png"):
        """convert this DFA to a PNG representation"""
        output = "digraph {rankdir=LR;node[shape=circle];\n"  # dot header

        # name the states
        names = {state: f"q{i}" for i, state in enumerate(self)}
        names[self.start_state] += "-"
        for state in self.final_states:
            names[state] += "\u00b1" if state is self.start_state else "+"

        # combine edge labels going to same state
        edge_labels = defaultdict(str)
        for state, paths in self.transitions.items():
            for symbol, to_state in paths.items():
                edge_labels[(state, to_state)] += symbol

        # write transitions to dot
        for (state, to_state), label in edge_labels.items():
            output += '"{}" -> "{}" [label="{}"];\n'.format(
                names[state], names[to_state], ",".join(label)
            )

        output += "}"
        dot_file = pydot.graph_from_dot_data(output)[0]
        dot_file.write_png(f"out/{file_name}")


def main():
    """quick tests"""
    dfa = DFA.from_atom("bab")
    dfa.to_png()


if __name__ == "__main__":
    main()
