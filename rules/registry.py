"""Basic registry for triple extraction rules. These read the input
templates file and preprocess them as required for triple extraction."""

_RULES = dict()


def register(name):
    """Registers a new triple extraction rule function under the given name."""

    def add_to_dict(func):
        _RULES[name] = func
        return func

    return add_to_dict


def get_extractor(data_src):
    """Fetches the triple extraction rules function"""
    return _RULES[data_src]
