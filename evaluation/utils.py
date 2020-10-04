def check_structured(extractions):
    """Confirms extractions are structured"""
    if not extractions:
        return True
    for ext in extractions:
        if not hasattr(ext, 'arg1'):
            return False
    return True

def check_unstructured(extractions):
    """Confirms extractions are unstructured."""
    if not extractions:
        return True
    for ext in extractions:
        if not hasattr(ext, 'args'):
            return False
    return True
