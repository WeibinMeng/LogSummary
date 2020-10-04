#import warnings
#warnings.filterwarnings("ignore")
from rouge import Rouge 
#from nltk.translate.bleu_score import sentence_bleu
rouge = Rouge()

class eval_unigram:
    def __init__(self):
        self.result = {'precision':0, 'recall':0, 'f_score':0, 'compression_rate':0}
        self.count = 0
        
    def evaluate_unigram(self, references:str, hypothesis:str):
        score = dict()
        self.count += 1
        #score['BLEU'] = 0
        score['ROUGE'] = {'f':0, 'p':0, 'r':0}
        if len(hypothesis) == 0:
            return score
        #score['BLEU'] = sentence_bleu([references.split()], hypothesis.split(), weights=(1,0,0,0))
        score['ROUGE'] = rouge.get_scores(references, hypothesis)[0]['rouge-1']
        self.result['precision'] += score['ROUGE']['p']
        self.result['recall'] += score['ROUGE']['r']
        self.result['f_score'] += score['ROUGE']['f']
        return score
    
    def record_compression_rate(self, hypothesis_length:int, doc_length:int):
        self.result['compression_rate'] += hypothesis_length / doc_length
    
    def get_result(self):
        if self.count == 0:
            return self.result
        temp = self.result.copy()
        temp['precision'] /= self.count
        temp['recall'] /= self.count
        temp['f_score'] /= self.count
        temp['compression_rate'] /= self.count
        return temp
    
    def clean_data(self):
        self.count = 0
        self.result = {'precision':0, 'recall':0, 'f_score':0, 'compression_rate':0}