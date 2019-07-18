"""
this module creates lexers and parsers for a particular grammar
"""
import re
from collections import namedtuple

from dfa import Dfa

Token = namedtuple("Token", "type value")
LexRule = namedtuple("LexRule", "experession handler")
ParseRule = namedtuple("ParseRule", "operator inputs handler")
OpPrecedence = namedtuple("OpPrecedence", "associativity operators")


def make_lexer(grammar):
    """creates a lexer with a particular grammar"""

    def lex(text):
        """ generate a series of tokens from an input string """
        while text:
            for rule in grammar:
                match = re.match(rule.expression, text)
                if match:
                    match_text = match.group()
                    token = rule.handler(match_text)
                    if token:
                        yield token
                    text = text[len(match_text) :]
                    break
            else:
                exit("could not lex" + text)

    return lex


def make_parser(rules, precedence):
    """creates a parser with a set of rules and precedence table"""

    def compare_precedence(op1, op2):
        """
        compares the precedence of two operators returns true if op1 has
        lower precedence than op2
        """
        prec1 = next((x for x in enumerate(precedence) if op1 in x[1].operators), None)
        prec2 = next((x for x in enumerate(precedence) if op2 in x[1].operators), None)
        return (
            prec1
            and prec2
            and (
                (prec1[0] < prec2[0])
                or (prec1[0] == prec2[0])
                and prec2[1].associativity == "right"
            )
        )

    def parse(tokens):
        """collapses token stream based on rules"""
        stack = []
        next_tok = next(tokens, None)
        while True:
            for rule in rules:
                n = len(rule.inputs)
                if (
                    rule.inputs != [t.type for t in stack[-n:]]
                    or rule.operator
                    and next_tok
                    and compare_precedence(rule.operator, next_tok.type)
                ):
                    continue
                stack[-n:] = [rule.handler(*stack[-n:])]
                break
            else:
                if next_tok:
                    stack.append(next_tok)
                    next_tok = next(tokens, None)
                elif len(stack) <= 1:
                    break
                else:
                    exit("error parsing" + str(stack))
        return stack[0].value

    return parse


def regex_to_dfa(pattern, alphabet):
    """build dfa from regex"""
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
            "atom", ["E", "E"], lambda l, r: Token("E", l.value.concatenate(r.value))
        ),
        ParseRule(
            "add",
            ["E", "add", "E"],
            lambda l, op, r: Token("E", l.value.union(r.value)),
        ),
    )

    tokens = make_lexer(token_types)(pattern)
    return make_parser(rule_table, precedence_table)(tokens)
