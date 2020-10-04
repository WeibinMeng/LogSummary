from .registry import register
from .utils import check_structured
from .evaluator import BaseEvaluator


def redundancy(extractions):
    num_partitions = len(set(extractions))
    num_pred = len(extractions)
    return num_partitions, num_pred


class RedundancyEvaluator(BaseEvaluator):
    def single_eval(self, extractions, groundtruth):
        if not check_structured(extractions):
            raise TypeError(
                "Structured extractions should be used as input for this evaluation method."
                )
        num_partitions, num_pred = redundancy(extractions)
        self.num_recalled += num_partitions
        self.num_extractions += num_pred
    
    def metrics(self):
        redundancy = self.num_extractions / self.num_recalled
        return {'Redundancy':redundancy}


@register("redundancy")
def build_eval(params):
    """ Returns (number of predicted triples / number of partitions)
    as a measure of redundancy. Partitions are obtained using He's 
    approach for equivalent extraction. The higher, the more redundant."""
    return RedundancyEvaluator(params)
