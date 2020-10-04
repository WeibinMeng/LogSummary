from abc import ABC, abstractmethod
from tqdm import tqdm


class BaseEvaluator(ABC):
    """
    """
    def __init__(self, params):
        self.params = params
        self.num_ok = 0
        self.num_extractions = 0
        self.num_recalled = 0
        self.num_gt = 0
    
    @abstractmethod
    def single_eval(self, extractions, groundtruth):
        """Evaluates a set of extractions versus their corresponding 
        ground truth"""
        pass

    def eval(self, results, groundtruth):
        """Evaluates the output as a whole considering various different
        templates and their corresponding triples"""
        for idx in tqdm(groundtruth, position=0, leave=True, desc="Eval"):
            self.single_eval(results[idx], groundtruth[idx])
        return self.metrics()

    def metrics(self):
        if self.num_extractions == 0  or self.num_gt == 0:
            print("Run a single evaluation first before getting metrics.")
            return None
        precision = self.num_ok / self.num_extractions
        recall = self.num_recalled / self.num_gt
        f1 = 2 * (precision * recall) / (precision + recall) if precision * recall > 0 else 0
        f2 = 5 * (precision * recall) / (4 * precision + recall) if precision * recall > 0 else 0
        return {'Precision':precision, 'Recall':recall, 'F1':f1, 'F2':f2}
