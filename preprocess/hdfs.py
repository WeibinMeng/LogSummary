from .registry import register
from .utils import (
    remove_brackets,
    split_on_punctuation,
)
import re
from .preprocessor import BasePreprocessor
from .globalConfig import regL


bgl_tag_pattern = re.compile('^([A-Z]+\s)')
def remove_log_type_tag(line):
    return re.sub(bgl_tag_pattern, '', line)


class HDFS_Preprocessor(BasePreprocessor):
    
    def _process_template(self, template):
        template = remove_log_type_tag(template)
        template = remove_brackets(template)
        parts = template.split(":")
        parts = split_on_punctuation(parts)
        return parts   

    def _process_log(self, log):
        idx, log = log.strip().split('\t')
        regexes = regL[self.params['log_type']]
        for regex in regexes:
            log = re.sub(regex, "", log)
        return log


@register("hdfs")
def preprocess_dataset(params):
    """
    Runs template preprocessing executor.
    """
    return HDFS_Preprocessor(params)
