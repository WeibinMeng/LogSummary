from .registry import register
from .utils import (
    remove_brackets,
    split_on_punctuation,
    remove_underscores,
)
import re
from .preprocessor import BasePreprocessor
from .globalConfig import regL


bgl_tag_pattern = re.compile(r'^([A-Z]+\s){2,}')
def remove_log_type_tag(line):
    return re.sub(bgl_tag_pattern, '', line)


colon_in_parentheses_pattern = re.compile(r'\(([^\(\)]+:[^\(\)]+)\)')
def subtract_parentheses_colon(line):
    result = re.findall(colon_in_parentheses_pattern, line)
    remaining = re.sub(colon_in_parentheses_pattern, '', line)
    if remaining:
        remaining = remaining.split(":")
        result.extend(remaining)
    return result


punctuation_split_pattern = re.compile(r'(?:\.|;)\s')
def split_on_punctuation(sentences):
    result = []
    for sentence in sentences:
        result.extend(re.split(punctuation_split_pattern, sentence))
    return result


class BGL_Preprocessor(BasePreprocessor):
    
    def _process_template(self, template):
        template = remove_log_type_tag(template)
        template = remove_underscores(template)
        sentences = subtract_parentheses_colon(template)
        sentences = split_on_punctuation(sentences)
        return sentences  

    def _process_log(self, log):
        idx, log = log.strip().split('\t')
        regexes = regL[self.params['log_type']]
        for regex in regexes:
            log = re.sub(regex, "", log)
        return log


@register("bgl")
def preprocess_dataset(params):
    """
    Runs template preprocessing executor.
    """
    return BGL_Preprocessor(params)
