from .registry import register
from ..oie_extraction.extraction import UnstructuredExtraction
import configparser
import os
import subprocess
from importlib.util import spec_from_file_location, module_from_spec
import sys
from .utils import text_file_to_list


# Loading configuration file
config = configparser.ConfigParser()    
config_path = os.path.join(
    os.path.dirname(__file__),
    'openie.ini',
)
config.read(config_path)


def module_from_file(module_name, file_path):
    """Imports a module given its path as 'module_name'.
    
    In this case we use it to import a whole package given the path to
    its __init__.py file.
    """
    spec = spec_from_file_location(module_name, file_path, submodule_search_locations=[])
    module = module_from_spec(spec)
    sys.modules[spec.name] = module 
    spec.loader.exec_module(module)
    print(spec.name)
    return module

#pylint: disable=unresolved-import
def get_props_func():
    """Imports PropS main function from its module"""
    global config
    module_from_file('external_props',config['PropS']['props_main_dir'])
    from external_props.applications.parse_props import main as props_func
    return props_func
#pylint: enable=unresolved-import    

def get_props_args(parsed_input_path):
    """Builds the arguments used for the imported PropS main function"""
    return {'--corenlp-json-input': True,
            '--dep': False,
            '--dontfilter': False,
            '--help': False,
            '--oie': True,
            '--original': False,
            '--tokenized': False,
            '-g': False,
            '-h': False,
            '-t': True,
            'FILE': open(parsed_input_path)}


def parse_input_stanford(input_remaining):
    global config
    # props uses Stanford CoreNLP modules for parsing its input
    stanford_jar_dir = os.path.normpath(config['Stanford']['dir'])
    jar = config['PropS']['stanford_jar']
    memory = config['PropS']['memory']
    properties_dir = config['PropS']['properties_dir']
    command = ["java",
            f"-{memory}",
            "-cp", f"{stanford_jar_dir}\\*",
            f"{jar}",
            "-annotators", "tokenize,ssplit,pos,parse",
            "-parse.flags", ' -makeCopulaHead',
            "-file", f"{input_remaining}",
            "-props", f"{properties_dir}\\stanford_parser.props",
            "-outputFormat", "json",
            "-parse.originalDependencies", 
            ]
    print(command)
    cp = subprocess.run(command)


def save_remaining(remaining, output_file):
    with open(output_file, 'w') as remaining_f:
        for idx in remaining:
            # remaining_idx = [idx for line in remaining[idx] if line]
            remaining_write = [line for line in remaining[idx] if line]
            remaining_f.writelines('\n'.join((*remaining_write,'')))


@register('props')
def extract_triples(input_remaining, params):
    output = './triples.txt'
    temp_source = './temp_remaining'
    save_remaining(input_remaining, temp_source)
    parse_input_stanford(temp_source)

    # Parsing with Stanford NLP as input for PropS
    stanford_parsed_file = os.path.abspath(f"{temp_source}.json")

    # Running PropS extraction
    arguments = get_props_args(stanford_parsed_file)
    props_func = get_props_func()
    extraction = props_func(arguments)
    props_extractions = []
    for propositions in extraction:
        sent_extractions = []
        for prop in propositions:
            args = [pair[1] for pair in prop.args]
            u_extraction = UnstructuredExtraction(
                pred=prop.pred,
                args=args,
            )
            sent_extractions.append(u_extraction)
        props_extractions.append(sent_extractions)

    # Getting a mapping for each line in the input to its template index
    idx_mapping = [idx for idx in input_remaining for line in input_remaining[idx] if line]

    extractions = {}
    remaining = {}
    for pos, propositions in enumerate(props_extractions):
        idx = idx_mapping[pos]
        extractions.setdefault(idx, []).extend(propositions)
    
    for idx in input_remaining:
        if idx not in extractions:
            remaining[idx] = input_remaining[idx]
            extractions[idx] = []
        else:
            remaining[idx] = []

    return extractions, remaining
