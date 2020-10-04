from .registry import register
from ..oie_extraction.extraction import Extraction
import configparser
import os
import subprocess
from .utils import text_file_to_list
import re


def run_clausie(input_source, output):
    config = configparser.ConfigParser()    
    config_path = os.path.join(
        os.path.dirname(__file__),
        'openie.ini',
    )
    config.read(config_path)
    jar_dir = os.path.normpath(config['ClausIE']['dir'])
    jar = os.path.join(
            jar_dir,
            config['ClausIE']['jar'],
            )
    memory = config['ClausIE']['memory']
    command = ["java",
            f"-{memory}",
            "-jar", f"{jar}",
            "-vf",f"{input_source}",
            "-o", f"{output}",
            ]
    print(command)
    cp = subprocess.run(command)


def save_remaining(remaining, output_file):
    line_to_idx_line = {}
    with open(output_file, 'w') as remaining_f:
        for idx in remaining:
            for line in remaining[idx]:
                remaining_f.write(f"{line}\n")
                line_to_idx_line[len(line_to_idx_line)] = (idx, line)
    return line_to_idx_line


triples_pattern = re.compile(r"^(\d+\t.+)")
def parse_clausie_triples(output_triples, line_to_idx_line):
    lines = text_file_to_list(output_triples)
    triples = {}
    for line in lines:
        match = re.search(triples_pattern, line)
        if match:
            text = match.group(1)
            splits = text.split('\t')
            idx = splits[0]
            tup = splits[1:]
            tup = tuple(part.strip('"') for part in tup)
            triple = Extraction.fromTuple(
                tup=tup,
                sentence=line_to_idx_line[int(idx) - 1][1]
            )
            triple_id = line_to_idx_line[int(idx) - 1][0]
            if triple_id in triples:
                triples[triple_id].append(triple)
            else:
                triples[triple_id] = [triple]
    return triples


@register('clausie')
def extract_triples(input_remaining, params):
    temp_source = os.path.join(params['id_dir'], 'temp_remaining.txt')
    line_to_idx_line = save_remaining(input_remaining, temp_source)
    output = os.path.join(params['id_dir'], 'triples.txt')
    run_clausie(temp_source, output)
    triples = parse_clausie_triples(output, line_to_idx_line)
    os.remove(temp_source)
    os.remove(output)
    remaining = {}
    for idx in input_remaining:
        if idx not in triples:
            remaining[idx] = input_remaining[idx]
            triples[idx] = []
        else:
            remaining[idx] = []
    return triples, remaining