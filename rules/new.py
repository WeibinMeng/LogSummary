from .registry import register
from .utils import power_strip
import re
from ..oie_extraction.extraction import Extraction


equals_triple_pattern = re.compile(r'([-\w\d\s]+)=\s*([\w\d\*]+)')
colon_triple_pattern = re.compile(r'([-\w\d\s]+):\s*([\w\d\*]+)')
def extract_triples_pattern(line, pattern=equals_triple_pattern):
    triples = []
    for name, var in re.findall(pattern, line):
        extraction = Extraction(
            arg1=power_strip(name),
            pred='is',
            arg2=var,
            sentence=line
        )
        triples.append(extraction)
    return triples


cli_variable_triple_pattern = re.compile(r'--(\S+)\s*(\S*)')
def extract_cli_triples(line):
    """Wraps the triple pattern extractor to allow for variables that
    are just flags. """
    triples = extract_triples_pattern(line, cli_variable_triple_pattern)
    for triple in triples:
        if not triple.arg2:
            triple.arg2 = 'set'
    return triples


# pattern to extract all parts within parentheses that contain a colon ":" or an equals "=" keeping what's inside
subtract_parentheses_pattern = re.compile(r'\((.*[:\=].*)\)')
def subtract_parentheses(line):
    result = re.findall(subtract_parentheses_pattern, line)
    remaining = power_strip(re.sub(subtract_parentheses_pattern, '', line))
    if remaining:
        result.append(remaining)
    return result


def pre_rules(template):
    remaining_output = []
    triples = []
    template = power_strip(template)
    parts = []

    # Checking for CLI formatted variables
    if "--" in template:
        triples_aux = extract_triples_pattern(template, pattern=cli_variable_triple_pattern)
        triples.extend(triples_aux)
        template = power_strip(re.sub(cli_variable_triple_pattern, '', template))
  
    has_equals = "=" in template
    has_colon = ":" in template
    if has_equals and not has_colon:
        # equals "=" means "is"
        triples_aux = extract_triples_pattern(template, pattern=equals_triple_pattern)
        triples.extend(triples_aux)
        remaining = power_strip(re.sub(equals_triple_pattern, '', template))
        if remaining:
            remaining_output.append(remaining)
    elif has_colon and not has_equals:
        # colon ":" means "is"
        triples_aux = extract_triples_pattern(template, pattern=colon_triple_pattern)
        triples.extend(triples_aux)
        remaining = power_strip(re.sub(colon_triple_pattern, '', template))
        if remaining:
            remaining_output.append(remaining)
    else:
        remaining_output.append(template)
    return triples, remaining_output


# this case is a colon that's not followed by a variable
colon_for_details_pattern = re.compile(r':(?:(?!\s*VAR))')

#splitting by full stop and colon where applicable
def pre_rules_old(template):
    split_output = []
    triples = []
    template = power_strip(template)
    parts = []

    # Checking for CLI formatted variables
    if "--" in template:
        triples_aux = extract_triples_pattern(template, pattern=cli_variable_triple_pattern)
        triples.extend(triples_aux)
        template = power_strip(re.sub(cli_variable_triple_pattern, '', template))

    # Splitting by punctuation and subtracting parentheses where applicable
    for part in re.split(r'\.|;', template):
        if re.search(r'[\(\)]', part):
            parts.extend(subtract_parentheses(part))
        else:
            parts.append(part)
    
    for part in parts:
        has_equals = "=" in part
        has_colon = ":" in part
        if not has_equals and not has_colon:
            split_output.append(power_strip(part))
        elif has_equals and not has_colon:
            triples_aux = extract_triples_pattern(part, pattern=equals_triple_pattern)
            triples.extend(triples_aux)
            remaining = power_strip(re.sub(equals_triple_pattern, '', part))
            if remaining:
                split_output.append(remaining)
        elif has_equals and has_colon:
            subparts = part.strip(':').split(':')
            for subpart in subparts:
                if "=" in subpart:
                    triples_aux = extract_triples_pattern(subpart, pattern=equals_triple_pattern)
                    triples.extend(triples_aux)
                    remaining = power_strip(re.sub(equals_triple_pattern, '', subpart))
                    if remaining:
                        split_output.append(remaining)
                else:
                    split_output.append(subpart.strip())
        elif has_colon and not has_equals:
            if re.search('VAR\d+\s*:\s*VAR', part):
                subparts = part.split(':')
            else:
                subparts = re.split(colon_for_details_pattern, part.strip(':'))
            for subpart in subparts:
                if ":" in subpart:
                    triples_aux = extract_triples_pattern(subpart, pattern=colon_triple_pattern)
                    triples.extend(triples_aux)
                    remaining = power_strip(re.sub(colon_triple_pattern, '', subpart))
                    if remaining:
                        split_output.append(remaining)
                else:
                    split_output.append(power_strip(subpart))
    return triples, split_output


@register("new")
def triple_rules_extractor(templates):
    """
    Runs triples extraction rules.
    """
    # TODO: may want to make this a separate function in utils and pass pre_rules
    triples = {}
    remaining = {}
    for idx, processed_templates in templates.items():
        for part in processed_templates:
            result = pre_rules(part)
            if idx in triples:
                triples[idx].extend(result[0])
                remaining[idx].extend(result[1])
            else:
                triples[idx] = result[0]
                remaining[idx] = result[1]
    return triples, remaining
