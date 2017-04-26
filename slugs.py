import re
from collections import Counter

from unidecode import unidecode
from toolz import curry, pipe

from sequencer import Items

WHITESPACE = re.compile(r'\s+')
NONALPHANUM = re.compile(r'[^\w_-]')


@curry
def trim(names, chars=None):
    return [i.strip(chars) for i in names]


def lowercase(names):
    return [i.lower() for i in names]


def deaccent(names):
    """Remove accents from characters."""
    return [unidecode(i) for i in names]


@curry
def sub(pattern, repl, names, count=0, flags=0):
    """Replace characters that match regular expression."""
    regex = re.compile(pattern, flags=flags)
    return [regex.sub(repl, i, count=count) for i in names]


@curry
def replace(old, new, names, count=-1):
    """Replace characters that match string."""
    return [i.replace(old, new, count) for i in names]


@curry
def whitespace(repl, names):
    """Replace whitespace."""
    return sub(WHITESPACE, repl, names)


@curry
def nonalphanums(repl, names):
    """Replace non-alphanumeric charaters."""
    return sub(NONALPHANUM, repl, names)


@curry
def numdups(names, fmt='{name}-{number}'):
    """Enumerate duplicate names."""
    duplicate = {k: v for k, v in Counter(names).items() if v > 1}
    for name, count in duplicate.items():
        for num in range(1, count + 1):
            idx = names.index(name)
            names[idx] = fmt.format(name=name, number=num)
    return names


def as_dict(original_names, names):
    """Map slugs to original names {slug-name: orig-name, ...}"""
    return dict(zip(names, original_names))


def slugify(names):
    tokens = Items(names)
    tokens.items = pipe(tokens.items, deaccent, trim, lowercase,
                        whitespace('_'), nonalphanums(''), numdups)
    return tokens.value
