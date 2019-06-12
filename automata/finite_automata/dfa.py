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

    @classmethod
    def from_atom(cls, atom, alphabet="ab"):
        """create a DFA from a string"""
        state = start_state = "q0"
        garbage = "q1"
        states = {start_state, garbage}
        transitions = {garbage: {symbol: garbage for symbol in alphabet}}

        for i, char in enumerate(atom, 2):
            new_state = f"q{i}"
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
            for letter in self.alphabet:
                neighbour = self.transitions[state, letter]
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    def __contains__(self, state):
        return state in self.states

    def complement(self):
        """return the complement of the dfa"""

        return DFA(
            set(self.states),
            self.alphabet,
            self.transitions.copy(),
            self.start_state,
            self.states - self.final_states,
        )

    def generate_dot(self, file_name="out.png"):
        """generate a dotfile corresponding to the FA"""
        # header
        output = "digraph {rankdir=LR;node[shape=circle];\n"

        names = {self.start_state: f"{self.start_state}-"}
        for state in self.states:
            suffix = ""
            if state is self.start_state:
                suffix = "-"
            if state in self.final_states:
                suffix = "\u00b1" if state is self.start_state else "+"
            names[state] = f"{state}{suffix}"

        # combine edge labels going to same state
        edge_labels = defaultdict(str)
        for state, paths in self.transitions.items():
            for symbol, to_state in paths.items():
                edge_labels[(state, to_state)] += symbol

        for (state, to_state), label in edge_labels.items():
            output += '"{}" -> "{}" [label="{}"];\n'.format(
                names[state], names[to_state], ",".join(label)
            )

        output += "}"
        dot_file = pydot.graph_from_dot_data(output)[0]
        dot_file.write_png(f"out/{file_name}")


def main():
    """tests"""
    # dfa = DFA(
    #     states={"q0", "q1", "q2"},
    #     alphabet="ab",
    #     transitions={
    #         "q0": {"a": "q0", "b": "q1"},
    #         "q1": {"a": "q0", "b": "q2"},
    #         "q2": {"a": "q2", "b": "q1"},
    #     },
    #     start_state="q0",
    #     final_states={"q1"},
    # )
    dfa = DFA.from_atom("abb")
    dfa.generate_dot()


if __name__ == "__main__":
    main()
