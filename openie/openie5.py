from .registry import register
import configparser
from ..oie_extraction.extraction import Extraction
from pyopenie import OpenIE5
import subprocess
import os
from .utils import text_file_to_list
import re

subtract_parentheses_pattern = re.compile('[\[\]]')
def clean_pred(pred):
    return re.sub(subtract_parentheses_pattern, '', pred)


# this function covers for the n-ary case as well as the binary and
# always outputs a binary triple
def get_triples(extractions):
    triples = []
    for extraction in extractions:
        for arg2 in extraction['extraction']['arg2s']:
            tup = (
                extraction['extraction']['arg1']['text'],
                clean_pred(extraction['extraction']['rel']['text']),
                arg2['text']
            )
            triple = Extraction.fromTuple(
                tup,
                sentence=extraction['sentence'],
                confidence=float(extraction['confidence'])
                )
            triples.append(triple)
    return triples


@register('openie5')
def extract_triples(input_remaining, params):
    config = configparser.ConfigParser()    
    config_path = os.path.join(
        os.path.dirname(__file__),
        'openie.ini',
    )
    config.read(config_path)
    port = config['OpenIE5']['port']
    extractor = OpenIE5(f'http://localhost:{port}')
    try:
        extractor.extract("This line checks if the server is running.")
    except Exception as e:
        print(e)
        print("OpenIE5 may not have been initialized")
        jar_dir = os.path.normpath(config['OpenIE5']['dir'])
        jar = os.path.join(
            jar_dir,
            config['OpenIE5']['jar'],
            )
        memory = config['OpenIE5']['memory']
        command = ["java",
            f"-{memory}",
            "-XX:+UseConcMarkSweepGC",
            "-jar", f'"{jar}"',
            "--httpPort", f"{port}",
            "--binary",  # the output is binary (arg1, rel, arg2)
            ]
        print("Please run the following command then restart the process:")
        print(' '.join(command))
        exit()
    
    triples = {}
    remaining = {}
    for idx in input_remaining:
        for line in input_remaining[idx]:
            extractions = []
            try:
                extractions = extractor.extract(line)
            except Exception as e:
                pass
            finally:
                extracted_triples = get_triples(extractions)
                # this way each idx in triples has an emptly list if no
                # triples are extracted, likewise for remaining
                if extracted_triples:
                    triples.setdefault(idx, []).extend(extracted_triples)
                    remaining[idx] = remaining.get(idx, [])
                else:
                    triples[idx] = triples.get(idx, [])
                    remaining.setdefault(idx, []).append(line)
    
    return triples, remaining
