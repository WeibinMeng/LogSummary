"""Basic registry for triples evaluation approaches."""

_METRIC = dict()


def register(name):
    """Registers a new triple evaluation approach under the given name."""

    def add_to_dict(func):
        _METRIC[name] = func
        return func

    return add_to_dict


def get_eval_metric(data_src):
    """Fetches the triple evaluation function associated with the given templates"""
    return _METRIC[data_src]
