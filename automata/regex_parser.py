"""
this module creates lexers and parsers for a particular grammar
"""
import re
from collections import namedtuple

# from dfa import Dfa

Token = namedtuple("Token", "type value")
LexRule = namedtuple("LexRule", "expression handler")
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
