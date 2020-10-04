from .registry import register
from .evaluator import BaseEvaluator


class CountsEvaluator(BaseEvaluator):
    def single_eval(self, extractions, groundtruth):
        self.num_gt += len(extractions)
        self.num_extractions += len(groundtruth)
    
    def metrics(self):
        return {'Expected triples':self.num_gt, 'Number of extractions':self.num_extractions}

@register("counts")
def build_eval(params):
    """ Returns the counts of expected and extracted triples."""
    return CountsEvaluator(params)
