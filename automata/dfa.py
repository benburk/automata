""" finite automaton class """
from collections import defaultdict

import pydot
from fsm import Fsm
from fsm import State
from regex_parser import LexRule
from regex_parser import make_lexer
from regex_parser import make_parser
from regex_parser import OpPrecedence
from regex_parser import ParseRule
from regex_parser import Token


class Dfa(Fsm):
    """
    a Deterministic Finite Automaton is a 5-tuple M=(Q,Σ,δ,q0,F) consisting of:
        - a finite set of states Q
        - a finite set of input symbols called the alphabet Σ
        - a transition function δ: Q × Σ → Q
        - an initial state q0 ∈ Q
        - a set of accept states F ⊆ Q
    """

    def __init__(
        self, states, alphabet, transitions, start_state, final_states
    ):  # pylint: disable-msg=too-many-arguments
        super().__init__(states, alphabet, start_state, final_states)
        self.transitions = transitions

    def __iter__(self):
        """iterate through the DFA using BFS"""
        visited = {self.start_state}
        queue = [self.start_state]
        while queue:
            state = queue.pop()
            yield state
            for symbol in self.alphabet:
                neighbour = self.transitions[state, symbol]
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    @classmethod
    def from_atom(cls, atom, alphabet="ab"):
        """create an FA from an atom"""
        state = start_state = State()
        garbage = State()
        states = {start_state, garbage}
        transitions = {(garbage, symbol): garbage for symbol in alphabet}

        for char in atom:
            new_state = State()
            for symbol in alphabet:
                transitions[state, symbol] = new_state if char == symbol else garbage
            state = new_state
            states.add(state)

        # have all edges from final state point to garbage state
        transitions.update({(state, symbol): garbage for symbol in alphabet})
        return cls(states, alphabet, transitions, start_state, {state})

    @classmethod
    def from_regex(cls, pattern, alphabet="ab"):
        """create a dfa from a regular expression"""
        token_types = (
            LexRule(r"\s+", lambda match: None),
            LexRule(fr'[{"".join(alphabet)}]', lambda match: Token("atom", match)),
            LexRule(r"\+", lambda match: Token("add", None)),
            LexRule(r"\*", lambda match: Token("star", None)),
            LexRule(r"[\^Λ]", lambda match: Token("null", "Λ")),
            LexRule(r"\(", lambda match: Token("(", None)),
            LexRule(r"\)", lambda match: Token(")", None)),
        )
        precedence_table = (
            OpPrecedence("left", ("add")),
            OpPrecedence("left", ("atom")),
            OpPrecedence("left", ("star")),
        )
        rule_table = (
            ParseRule(
                None, ["atom"], lambda n: Token("E", Dfa.from_atom(n.value, alphabet))
            ),
            ParseRule(None, ["(", "E", ")"], lambda l, ex, r: ex),
            ParseRule(
                "star", ["E", "star"], lambda l, op: Token("E", l.value.kleene_star())
            ),
            ParseRule(
                "atom",
                ["E", "E"],
                lambda l, r: Token("E", l.value.concatenate(r.value)),
            ),
            ParseRule(
                "add",
                ["E", "add", "E"],
                lambda l, op, r: Token("E", l.value.union(r.value)),
            ),
        )

        tokens = make_lexer(token_types)(pattern)
        return make_parser(rule_table, precedence_table)(tokens)

    def accepts(self, string):
        """ check whether this DFA accepts a particular string """
        state = self.start_state
        for char in string:
            state = self.transitions[state, char]
        return state in self.final_states

    def complement(self):
        """return a DFA that is the complement of this DFA"""
        states = {x: State() for x in self.states}
        transitions = {
            (states[state], symbol): states[to_state]
            for (state, symbol), to_state in self.transitions.items()
        }
        final_states = {states[state] for state in self.states - self.final_states}

        return Dfa(
            set(states.values()),
            self.alphabet,
            transitions,
            states[self.start_state],
            final_states,
        )

    def union(self, other):
        """return the union of this DFA with another"""
        start_label = frozenset([self.start_state, other.start_state])
        states = {start_label: State()}  # maps a label to its new state
        transitions = dict()
        final_states = set()

        boundary = {start_label}
        while boundary:
            label = boundary.pop()
            if any(x in self.final_states | other.final_states for x in label):
                final_states.add(states[label])

            merged_transitions = {**self.transitions, **other.transitions}
            for symbol in self.alphabet:
                # build next label
                next_label = [merged_transitions[x, symbol] for x in label]
                next_label = frozenset(next_label)
                # create state for new labels
                if next_label not in states:
                    states[next_label] = State()
                    boundary.add(next_label)

                transitions[states[label], symbol] = states[next_label]

        return Dfa(
            set(states.values()),
            self.alphabet,
            transitions,
            states[start_label],
            final_states,
        )

    def kleene_star(self):
        """ return an FA that is the kleene closure of this FA """
        start_label = frozenset([self.start_state])
        states = {start_label: State()}
        transitions = dict()
        final_states = {states[start_label]}

        boundary = {start_label}
        while boundary:
            label = boundary.pop()
            if any(x in self.final_states for x in label):
                final_states.add(states[label])

            for symbol in self.alphabet:
                # build next label
                next_label = [self.transitions[x, symbol] for x in label]
                if any(x in self.final_states for x in next_label):
                    next_label.append(self.start_state)
                next_label = frozenset(next_label)
                # create state for new labels
                if next_label not in states:
                    states[next_label] = State()
                    boundary.add(next_label)

                transitions[states[label], symbol] = states[next_label]

        return Dfa(
            set(states.values()),
            self.alphabet,
            transitions,
            states[start_label],
            final_states,
        )

    def concatenate(self, other):
        """ return an FA that is the concatenation of this FA with other """
        start_label = [self.start_state]
        if self.start_state in self.final_states:
            start_label.append(other.start_state)
        start_label = frozenset(start_label)

        states = {start_label: State()}
        transitions = dict()
        final_states = set()

        boundary = {start_label}
        while boundary:
            label = boundary.pop()
            if any(x in other.final_states for x in label):
                final_states.add(states[label])

            for symbol in self.alphabet:
                # build next label
                merged_transitions = {**self.transitions, **other.transitions}
                next_label = [merged_transitions[x, symbol] for x in label]
                if any(x in self.final_states for x in next_label):
                    next_label.append(other.start_state)
                next_label = frozenset(next_label)
                # create state for new labels
                if next_label not in states:
                    states[next_label] = State()
                    boundary.add(next_label)

                transitions[states[label], symbol] = states[next_label]

        return Dfa(
            set(states.values()),
            self.alphabet,
            transitions,
            states[start_label],
            final_states,
        )

    def intersect(self, other):
        """ return an FA that is the intersection of this FA with other """
        start_label = frozenset([self.start_state, other.start_state])
        states = {start_label: State()}  # maps a label to its new state
        transitions = dict()
        final_states = set()

        boundary = {start_label}
        while boundary:
            label = boundary.pop()
            if all(x in self.final_states | other.final_states for x in label):
                final_states.add(states[label])

            for symbol in self.alphabet:
                # build next label
                merged_transitions = {**self.transitions, **other.transitions}
                next_label = [merged_transitions[x, symbol] for x in label]
                next_label = frozenset(next_label)
                # create state for new labels
                if next_label not in states:
                    states[next_label] = State()
                    boundary.add(next_label)

                transitions[states[label], symbol] = states[next_label]

        return Dfa(
            set(states.values()),
            self.alphabet,
            transitions,
            states[start_label],
            final_states,
        )

    def to_png(self, file_name="out.png"):
        """ generate a dotfile corresponding to the FA """
        # header
        output = "digraph {rankdir=LR;node[shape=circle];\n"

        # name the states
        names = {state: f"q{i}" for i, state in enumerate(self)}
        for state in self.final_states:
            names[state] += "\u00b1" if state is self.start_state else "+"

        # combine edge labels going to same state
        edge_labels = defaultdict(str)
        for (from_state, symbol), to_state in self.transitions.items():
            edge_labels[(from_state, to_state)] += symbol

        # write the edges
        for (start, end), label in edge_labels.items():
            label = ",".join(sorted(label))
            output += f'"{names[start]}"->"{names[end]}" [label="{label}"];\n'

        output += "}"
        dot_file = pydot.graph_from_dot_data(output)[0]
        dot_file.write_png("out/" + file_name)


def main():
    """ the main method leave me alone pylint """
    # dfa = Dfa.from_atom("bab")
    # dfa = dfa.complement()
    # dfa.to_png()

    dfa = Dfa.from_regex("b*a")
    dfa.to_png()


if __name__ == "__main__":
    main()
