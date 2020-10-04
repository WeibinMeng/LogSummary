import re


brackets = re.compile(r'[\[\]\{\}\(\)]')
def remove_brackets(line):
    return re.sub(brackets, ' ', line).strip()


# Some variables use underscores which we want to keep so we only remove
# the ones from longer sentences
underscores = re.compile(r'([\w\d]+_[\w\d]+){3,}')
def remove_underscores(line):
    return re.sub(underscores, removing_underscores, line)
def removing_underscores(match):
    group = match.group()
    return group.replace('_', ' ')


punctuation_split_pattern = re.compile(r'(?:\.|;|\!)\s')
def split_on_punctuation(sentences):
    result = []
    for sentence in sentences:
        result.extend(re.split(punctuation_split_pattern, sentence))
    return result
