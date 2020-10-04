from .registry import register
from .utils import check_structured
from .evaluator import BaseEvaluator


def he(extractions, gt):
    extractions = set(extractions)
    gt = set(gt)
    num_ok = len(gt.intersection(extractions))
    num_extractions = len(extractions)
    num_gt = len(gt)
    return num_ok, num_extractions, num_ok, num_gt


def he_2(extractions, gt):
    recalled_gt = set()
    correct_ext = set()
    for e_idx, ext in enumerate(extractions):
        for g_idx, gt_ext in enumerate(gt):
            if ext == gt_ext:
                recalled_gt.add(g_idx)
                correct_ext.add(e_idx)
    num_extractions = len(extractions)
    num_gt = len(gt)
    num_ok = len(correct_ext)
    num_recalled = len(recalled_gt)
    return num_ok, num_extractions, num_recalled, num_gt
    

class HeEvaluator(BaseEvaluator):
    def single_eval(self, extractions, groundtruth):
        if not (check_structured(extractions) and check_structured(groundtruth)):
            raise TypeError(
                "Structured extractions should be used as input for this evaluation method."
                )
        if not extractions and not groundtruth:
            num_ok = num_extractions = num_recalled = num_gt = 1
        else:
            num_ok, num_extractions, num_recalled, num_gt =\
                he_2(extractions, groundtruth)
        self.num_ok += num_ok
        self.num_gt += num_gt
        self.num_extractions += num_extractions
        self.num_recalled += num_recalled


@register("he")
def build_eval(params):
    """ This approach considers partitioning for each template, both the 
    results and the ground truth in groups that are equivalent according
    to He's approach. Two triples are equivalent if the syntactic heads
    of their predicates and arguments match."""
    return HeEvaluator(params)