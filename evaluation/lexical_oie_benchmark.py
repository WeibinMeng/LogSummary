# https://github.com/gabrielStanovsky/oie-benchmark/blob/master/benchmark.py
# https://github.com/gabrielStanovsky/oie-benchmark/blob/master/matcher.py
from .registry import register
from .utils import check_unstructured
from .evaluator import BaseEvaluator
from ..oie_extraction.extraction import UnstructuredExtraction
unstructure_extractions = UnstructuredExtraction.unstructure_extractions 

LEXICAL_THRESHOLD = 0.25 # Same as theirs


def lexical(extractions, gt):
    correct_ext = set()
    recalled_gt = set()
    for e_idx, ext in enumerate(extractions):
        for g_idx, gt_ext in enumerate(gt):
            pred_res = ext.pred.strip().split()
            gt_res = gt_ext.pred.strip().split()
            if not set(pred_res).intersection(set(gt_res)):
                continue
            count_match = 0      
            for w1 in gt_ext.args:
                for w2 in ext.args:
                    if w1 == w2:
                        count_match += 1
            coverage = count_match / len(gt_ext.args) if gt_ext.args else 0

            # Counting differently for precision than for recall
            # Precision is for the extracted triples and recall is
            # for the ground truth triples
            if coverage > LEXICAL_THRESHOLD:
                recalled_gt.add(str(g_idx))
                correct_ext.add(str(e_idx)) 
    num_ok = len(correct_ext)
    num_recalled = len(recalled_gt)
    num_extractions = len(extractions)
    num_gt = len(gt)
    return num_ok, num_extractions, num_recalled, num_gt


class LexicalEvaluator(BaseEvaluator):
    def single_eval(self, extractions, groundtruth):
        if not (check_unstructured(extractions) and  check_unstructured(groundtruth)):
            extractions = unstructure_extractions(extractions)
            groundtruth = unstructure_extractions(groundtruth)
        if not extractions and not groundtruth:
            num_ok = num_extractions = num_recalled = num_gt = 1
        else:
            num_ok, num_extractions, num_recalled, num_gt =\
                lexical(extractions, groundtruth)
        self.num_ok += num_ok
        self.num_gt += num_gt
        self.num_extractions += num_extractions
        self.num_recalled += num_recalled



@register("lexical")
def build_eval(params):
    """ This approach matches two extractions if their predicates 
    overlap in at least one word and if their arguments matching number
    of words percentage is above the lexical threshold."""
    return LexicalEvaluator(params)