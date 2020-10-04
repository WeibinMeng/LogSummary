"""Basic registry for log template preprocessors. These read the input
templates file and preprocess them as required for triple extraction."""

_PREPROCESSORS = dict()


def register(name):
    """Registers a new log template preprocessor function under the given name."""

    def add_to_dict(func):
        _PREPROCESSORS[name] = func
        return func

    return add_to_dict


def get_preprocessor(data_src):
    """Fetches the log template preprocessor function associated with the given templates"""
    return _PREPROCESSORS[data_src]
