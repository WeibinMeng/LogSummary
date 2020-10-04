"""Basic registry for OpenIE approaches. These extract triples from
natural language sentences."""

_OPENIE = dict()


def register(name):
    """Registers a new OpenIE approach under the given name."""

    def add_to_dict(func):
        _OPENIE[name] = func
        return func

    return add_to_dict


def get_extractor(data_src):
    """Fetches the target OpenIE approach function."""
    return _OPENIE[data_src]
