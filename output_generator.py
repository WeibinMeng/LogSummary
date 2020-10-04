from .matchTree import MatchTree
import re


varx_pattern = re.compile(r'VAR(\d+)')    
class ReplVarX:
    def __init__(self, variables, triples, tag=True):
        self.variables = variables
        self.triples = triples
        self.tag = tag
    def __call__(self, match=None):
        var_idx = int(match.group(1)) - 1
        # tagging variablas as [([VAR])]
        if var_idx < len(self.variables):
            if self.tag:
                return f'[([{self.variables[var_idx]}])]'
            else:
                return f'{self.variables[var_idx]}'
        else:
            return ''


class OutputGenerator:
    def __init__(self, templates):
        self.templates = templates
        self.__build_template_tree()
    
    def __build_template_tree(self):
        self.matcher = MatchTree()
        for idx, template in self.templates.items():
            self.matcher.add_template(template.split(), idx)

    def __get_vars_list(self, template_idx, log):
        """
        Gets the variables in the template from the logs limited to
        the ones represented by asterisks ('*') only.
        These are the only ones being considered in the triples.
        # As the pointers advance on both the log and the template
        # the variables are only collected when * is encountered on
        # the template
        """
        template = self.templates[template_idx].split()
        log = log.split()
        variables = []
        pt = pl = 0
        while pt < len(template) and pl < len(log):
            if template[pt] == log[pl]:
                pt += 1
                pl += 1
                continue
            elif template[pt] == '*':
                # found a variable
                while pt < len(template) and template[pt] == '*':
                    # in case there are many variables together
                    pt += 1
                if pt >= len(template):
                    # it's the end of the template
                    variables.append(' '.join(log[pl:]))
                    break
                else:
                    variable_tokens = []
                    while pl < len(log) and log[pl] != template[pt]:
                        variable_tokens.append(log[pl])
                        pl += 1
                    # it duplicates when many variables together for a correct output
                    variables.append(' '.join(variable_tokens))
            else:
                # it is a variable not covered by the template asterisks
                # we move on on the log but stay on the template token
                pl += 1
        return variables
    
    def replace_variables(self, variables, triples, tag=True):
        repl_varx = ReplVarX(variables, triples, tag)
        for triple in triples:
            triple.pred = re.sub(varx_pattern, repl_varx, triple.pred)
            if hasattr(triple, 'arg1'):
                triple.arg1 = re.sub(varx_pattern, repl_varx, triple.arg1)
                triple.arg2 = re.sub(varx_pattern, repl_varx, triple.arg2)
            else:
                triple.args = list(map(
                    lambda x: re.sub(varx_pattern, repl_varx, x),
                    triple.args,
                    ))
    
    def generate_output(self, log, triples, tag=True):
        idx, _ = self.matcher.match_template(log.split())
        idx = str(idx)
        if idx is not None and idx in triples and triples[idx]:
            variables = self.__get_vars_list(idx, log)
            triples_set = [triple.copy() for triple in triples[idx]]
            self.replace_variables(variables, triples_set, tag)
            return triples_set
        return []
