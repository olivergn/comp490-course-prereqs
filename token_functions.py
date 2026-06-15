import re


def tokenize(expr):
    tokens = re.split(r'(\(|\)|\band\b|\bor\b)', expr)
    return [t.strip() for t in tokens if t and t.strip()]

def parse_tokens(tokens):
    tokens = tokens[::-1]

    def parse_or():
        left = parse_and()
        while tokens and tokens[-1] == 'or':
            tokens.pop()
            right = parse_and()
            left = ('or', left, right)
        return left
    
    def parse_and():
        left = parse_atom()
        while tokens and tokens[-1] == 'and':
            tokens.pop()
            right = parse_atom()
            left = ('and', left, right)
        return left
    
    def parse_atom():
        token = tokens.pop()
        if token == '(':
            node = parse_or()
            tokens.pop()
            return node
        return token
    
    return parse_or()

def collapse_tokens(tokens):
    if isinstance(tokens, str):
        return tokens
    
    label, left_raw, right_raw = tokens
    left = collapse_tokens(left_raw)
    right = collapse_tokens(right_raw)

    left_label = None if isinstance(left, str) else left[0]
    right_label = None if isinstance(right, str) else right[0]

    new_tokens = (label,)

    if label == left_label:
        new_tokens += left[1:]
    else:
        new_tokens += (left,)
    
    if label == right_label:
        new_tokens += right[1:]
    else:
        new_tokens += (right,)
    
    return new_tokens
