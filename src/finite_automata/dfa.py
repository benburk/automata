"""Deterministic Finite Automata"""
from collections import defaultdict
import pydot


class DFA:
    """Deterministic Finite Automata"""

    def __init__(self, states, alphabet, transitions, start_state, final_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def __iter__(self):
        visited = {self.start_state}
        queue = [self.start_state]
        while queue:
            state = queue.pop()
            yield state
            for letter in self.alphabet:
                neighbour = self.transitions[state, letter]
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    def __contains__(self, state):
        return state in self.states

    def generate_dot(self, file_name="out.png"):
        """ generate a dotfile corresponding to the FA """
        # header
        output = "digraph {rankdir=LR;node[shape=circle];\n"

        # combine edge labels going to same state
        edge_labels = defaultdict(str)
        for state, paths in self.transitions.items():
            for symbol, to_state in paths.items():
                edge_labels[(state, to_state)] += symbol

        for (state, to_state), label in edge_labels.items():
            output += f"\"{state}\" -> \"{to_state}\" [label={','.join(label)}];\n"

        output += "}"
        dot_file = pydot.graph_from_dot_data(output)[0]
        dot_file.write_png(file_name)


def main():
    """tests"""
    dfa = DFA(
        states={"q0", "q1", "q2"},
        alphabet={"0", "1"},
        transitions={
            "q0": {"0": "q0", "1": "q1"},
            "q1": {"0": "q0", "1": "q2"},
            "q2": {"0": "q2", "1": "q1"},
        },
        start_state="q0",
        final_states={"q1"},
    )
    dfa.generate_dot()


if __name__ == "__main__":
    main()
