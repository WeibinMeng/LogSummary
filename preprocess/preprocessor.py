from abc import ABC, abstractmethod
import json
from ..oie_extraction.extraction import Extraction
from tqdm import tqdm


class BasePreprocessor(ABC):
    """ Abstract class to be implemented by all processors.

    Methods
    -------
    process_templates(self, **kwargs)
        Abstract method for the subclass to implement how the templates
        of the corresponding type should be processed.
    process_logs(self, **kwargs)
        Idem for logs.
    """
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def _process_template(self, log):
        """Processes a single template line uniquely to each log type
        on top of what process_templates function does."""
        pass

    @abstractmethod
    def _process_log(self, log):
        """Processes a single log line."""
        pass
    
    class Repl:
        def __init__(self, ini=0):
            self.called = ini
        def __call__(self, match=None):
            self.called += 1
            return f'VAR{self.called}'

    def substitute_vars(self, template):
        tokens = template.strip().split()
        namer = BasePreprocessor.Repl()
        return ' '.join([namer() if token == '*' else token for token in tokens])
    
    def remove_duplicate_asterisks(self, template):
        template = template.strip().split()
        result = []
        pt = 0
        while pt < len(template):
            result.append(template[pt])
            if template[pt] == '*':
                while pt < len(template) and template[pt] == '*':
                    # getting rid of contiguous asterisks
                    pt += 1
            else:
                pt += 1
        return ' '.join(result)

    def process_templates(self):
        input_source = self.params['templates']
        with open(input_source, 'r') as f:
            gt = json.load(f)
        processed_templates = {}
        improved_templates = {}
        online_templates = {}
        gt_triples = {}
        for idx in gt:
            improved_templates[idx] = self.remove_duplicate_asterisks(gt[idx][1])
            online_templates[idx] = self.remove_duplicate_asterisks(gt[idx][0])
            logie_template = self.substitute_vars(online_templates[idx])
            processed_parts = self._process_template(logie_template)
            triples = gt[idx][2]
            if triples:
                triples = [Extraction.fromTuple(tup, sentence=logie_template)
                        for tup in triples]
            gt_triples[idx] = [triple for triple in triples if triple.pred]
            processed_templates[idx] = [part for part in processed_parts if part] 
        return processed_templates, gt_triples, improved_templates, online_templates

    def process_logs(self):
        """Returns generator from the raw log file and yields a log as
        it's processed"""
        input_source = self.params['raw_logs']
        with open(input_source, 'r', encoding='latin-1') as IN:
            line_count = sum(1 for line in IN)
        with open(input_source, 'r', encoding='latin-1') as logs_file:
            for log in tqdm(logs_file, total=line_count):
                yield self._process_log(log)
