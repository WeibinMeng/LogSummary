from .registry import register
import configparser
import os
import pathlib
from shutil import copyfile
from ..oie_extraction.extraction import Extraction
from .utils import text_file_to_list
import re


def parse_triples_reverb_format(lines):
# Reverb format https://github.com/knowitall/reverb/blob/master/README.md
    result = {}
    for line in lines:
        line = line.strip().split('\t')
        idx = line[1]
        triple = (line[2:5])
        extraction = Extraction.fromTuple(
            triple,
            sentence=line[12],
            confidence=float(line[11])
            )
        result.setdefault(idx, []).append(extraction)
    return result


def parse_remaining_reverb_format(lines, triples):
    remaining = {}
    # use count while the idx is not the ordinal of the template
    # this is to see which templates didn't yield triples
    for i, line in enumerate(lines):
        if str(i) not in triples:
            line = line.strip()
            remaining[i] = [line]
    return remaining


def clean_temp_file(file_name):
    lines = text_file_to_list(file_name)
    remove_index = re.compile(r'^\d+\t')
    with open(file_name, 'w') as f:
        for line in lines:
            sentence = re.sub(remove_index,'',line)
            f.write(sentence)


def save_remaining(remaining, output_file):
    with open(output_file, 'w') as remaining_f:
        for idx in remaining:
            remaining_idx = remaining[idx]
            remaining_idx = [f'{idx}\t{line}' for line in remaining_idx if len(line.split())>1]
            remaining_f.writelines('\n'.join((*remaining_idx,'')))


@register('stanford')
def extract_triples(input_remaining, params):
    output = './triples.txt'
    # the java app uses a file as an input so the remaining input is
    # saved into a temporary file 
    temp_source = './temp_remaining.txt'
    save_remaining(input_remaining, temp_source)
    # the indexing from the Stanford CoreNLP ReVerb format output uses
    # the ordinal of the sentence so I clean the original index but keep
    # it in a separate temporary file
    temp_file_name = './temp_source.txt'
    copyfile(temp_source, temp_file_name)
    # We need to clean it so that Stanford CoreNLP has a clean sentence
    # per line in the input file
    clean_temp_file(temp_file_name)
    # parsing config
    config = configparser.ConfigParser()
    config_path = os.path.join(
        os.path.dirname(__file__),
        'openie.ini',
    )
    config.read(config_path)
    jars_dir = os.path.normpath(config['Stanford']['dir'])
    memory = config['Stanford']['memory']
    program = config['Stanford']['program']
    # checkout https://github.com/stanfordnlp/CoreNLP/issues/789
    # to see if they fixed how to use -resolve_coref true in the command
    # See https://stackoverflow.com/questions/35075463/corenlp-tokenizer-sentence-splitter-misbehaves-on-html-input
    # To understand the reason why behind tokenizePerLine and eolonly
    command = f'java -{memory} -cp "{jars_dir}\\*" {program}\
        -threads 8\
        -tokenize.options tokenizePerLine\
        -ssplit.eolonly true\
        -triple.all_nominals true -format reverb "{temp_file_name}"\
        > "{output}"'
    print(command)
    print("Extracting triples with StanfordNLP...")
    code = os.system(command)
    # removing temporary file
    os.remove(temp_file_name)
    if code == 0:
        # parsing results into dicts
        stanford_triples = text_file_to_list(output)
        stanford_triples = parse_triples_reverb_format(stanford_triples)
        stanford_remaining = text_file_to_list(temp_source)
        stanford_remaining = parse_remaining_reverb_format(stanford_remaining, stanford_triples)

        # obtaining a mapping of each line in the output triples from
        # reverb format to the original source template idx
        # note reverb outputs original line ordinal as the id instead
        stanford_to_idx = [line.split('\t')[0] for line in text_file_to_list(temp_source)]

        triples_output = {}
        remaining_output = {}
        # the i is the line number which is how stanford indexes the triples
        # there may be several triples from the sentence of each line
        # from the source file we build a mapping from the line to the actual
        # template index to gather all the triples for it
        for i, actual_idx in enumerate(stanford_to_idx):
            triples_output.setdefault(actual_idx, []).extend(stanford_triples.get(str(i), []))
            remaining_output.setdefault(actual_idx, []).extend(stanford_remaining.get(str(i), []))
        
        for idx in input_remaining:
            if idx not in triples_output:
                remaining_output[idx] = input_remaining[idx]
                triples_output[idx] = []
            else:
                remaining_output[idx] = []

        # removing the temporary file that was created
        os.remove(temp_source)
        return triples_output, remaining_output
    else:
        # removing the temporary file that was created
        os.remove(temp_source)
        raise RuntimeError("Standford CoreNLP OpenIE FAILED")
    