# Adapted from https://github.com/hltcoe/PredPatt/blob/master/predpatt/patt.py
from .registry import register
from ..oie_extraction.extraction import Extraction
from predpatt import PredPatt, PredPattOpts
from predpatt.util.ud import dep_v1, postag
from predpatt.patt import Argument
import spacy
__nlp = spacy.load('en_core_web_sm')

(NORMAL, POSS, APPOS, AMOD) = ("normal", "poss", "appos", "amod")


def sort_by_position(x):
    return list(sorted(x, key=lambda y: y.position))


def format_predicate(predicate):
    ret = []
    args = predicate.arguments

    if predicate.type == POSS:
        raise Exception('POSS case! Check it out')
        return (args[0].phrase(), POSS, args[1])
    
    if predicate.type in {AMOD, APPOS}:
        # Special handling for `amod` and `appos` because the target
        # relation `is/are` deviates from the original word order.
        arg0 = None
        other_args = []
        for arg in args:
            if arg.root == predicate.root.gov:
                arg0 = arg
            else:
                other_args.append(arg)
        relation = 'is'
        if arg0 is not None:
            ret = [arg0.phrase(), relation]
            args = other_args
        else:
            ret = [args[0].phrase(), relation]
            args = args[1:]

    if ret:
        return (
            ret[0], 
            ret[1],
            ' '.join(
                    [token.text for token in predicate.tokens]\
                    + [a.phrase() for a in args]
                    )
                )
    
    # Mix arguments with predicate tokens. Use word order to derive a
    # nice-looking name.
    arg1 = []
    pred = []
    arg2 = []
    elems = sort_by_position(predicate.tokens + args)
    for i, y in enumerate(elems):
        if isinstance(y, Argument) and i == 0:
            arg1 = [y.phrase()]
            if (predicate.root.gov_rel == predicate.ud.xcomp and
                predicate.root.tag not in {postag.VERB, postag.ADJ} ):
                pred = ['is']
        else:
            if isinstance(y, Argument):
                if pred:
                    arg2.extend([a.phrase() if isinstance(a, Argument) else a.text for a in elems[i:]])
                    break
                else:
                    arg1.append(y.phrase())
            else:
                pred.append(y.text)

    return (' '.join(arg1), ' '.join(pred), ' '.join(arg2))


def get_predpatt_triples(predpatt_output, line):
    triples = []
    for pred in predpatt_output.instances:
        tup = format_predicate(pred)
        if not tup[2]:
            # splitting predicates without arg2 where appropriate 
            tup = list(tup)
            doc = __nlp(tup[1])
            split = len(tup[1])
            for i, token in enumerate(doc):
                if token.pos_ not in ['AUX','VERB','ADP','ADV']:
                    split = i
                    break
            tup[1] = [token.text for token in doc]
            tup[2] = ' '.join(tup[1][split:])
            tup[1] = ' '.join(tup[1][:split])
            if not tup[1]:
                tup[1], tup[2] = tup[2], tup[1]
        triple = Extraction.fromTuple(
            tup=tup,
            sentence=line,
        )
        triples.append(triple)
    return triples


@register('predpatt')
def extract_triples(input_remaining, params):
    opts = PredPattOpts(
            resolve_relcl = True,  # relative clauses
            resolve_appos = True,  # appositional modifiers
            resolve_amod = True,   # adjectival modifiers
            resolve_conj = True,   # conjuction
            resolve_poss = True,   # possessives
            ud = dep_v1.VERSION,   # the version of UD
            )
    triples = {}
    remaining = {}
    for idx in input_remaining:
        for line in input_remaining[idx]:
            if line.strip():
                try:
                    pp = PredPatt.from_sentence(line, opts=opts, cacheable=False)
                    extractions = get_predpatt_triples(pp, line)
                    if extractions:
                        triples.setdefault(idx, []).extend(extractions)
                except KeyError:
                    pass
        if idx not in triples:
            remaining[idx] = input_remaining[idx]
            triples[idx] = []
    return triples, remaining
