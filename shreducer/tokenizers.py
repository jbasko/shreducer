import shlex


class _SpecialMarker(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<{}_VALUE>'.format(self.name.upper())


EOF = 'EOF'
EOF_VALUE = _SpecialMarker(EOF)

BOF = 'BOF'
BOF_VALUE = _SpecialMarker(BOF)


def create_shlex_tokenizer(with_eof=False, with_bof=False, **settings):
    """
    See what attributes can be set on shlex:
    https://docs.python.org/2/library/shlex.html#shlex-objects

    For example, for simple arithmetic parsers you probably want to add dot "." to wordchars:
        custom_tokenizer(..., wordchars=string.digits + '.')
    """
    def custom_tokenizer(input_str):
        tokenizer = shlex.shlex(input_str)
        if with_bof:
            yield BOF_VALUE
        for k, v in settings.items():
            setattr(tokenizer, k, v)
        for t in tokenizer:
            yield t
        if with_eof:
            yield EOF_VALUE
    return custom_tokenizer
