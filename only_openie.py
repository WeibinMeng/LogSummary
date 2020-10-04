from .evaluation import registry as eval_registry
from .openie import registry as openie_registry
from .rules import registry as rules_registry
from .preprocess import registry as preprocess_registry
from .utils import (
    file_handling,
    print_params,
    save_results,
    save_global_output_triples,
    save_log_triples,
    Timing
)
from .init_params import init_main_args, parse_main_args
from .utils import combine_extractions, remove_varx
from .output_generator import OutputGenerator
import os


def init_args():
    """Init command line args used for configuration."""

    parser = init_main_args()
    return parser.parse_args()


def parse_args(args):
    """Parse provided args for runtime configuration."""
    params = parse_main_args(args)
    return params


def turn_rawlogs_into_oie_input(logs):
    for idx, log in enumerate(logs, 1):
        yield str(idx), [log]


def main():
    # Init params
    params = parse_args(init_args())
    print_params(params)
    file_handling(params)
    # Load data: templates and ground truth for evaluation
    preprocessor_getter = preprocess_registry.get_preprocessor(params['log_type'])
    preprocessor = preprocessor_getter(params)
    _, ground_truth, improved_templates, online_templates =\
        preprocessor.process_templates()
     # Run openie triples extraction
    openie_extractor = openie_registry.get_extractor(params['openie'])
    if 'raw_logs' in params:
        # Producing desired output for logs input
        gt_output_generator = OutputGenerator(improved_templates)
        processed_logs = preprocessor.process_logs()
        oie_input_gen = turn_rawlogs_into_oie_input(processed_logs)
        oie_input = {}
        log_ground_truth = {}
        for idx, log in oie_input_gen:
            oie_input[idx] = log
            gt_output =  gt_output_generator.generate_output(log[0], ground_truth, tag=params['tag'])
            log_ground_truth[idx] = gt_output
        global_result, oie_remaining = openie_extractor(oie_input, params)

        for eval_metric in params['evaluation']:
            get_evaluator = eval_registry.get_eval_metric(eval_metric)
            evaluator = get_evaluator(params)
            evaluator.eval(global_result, log_ground_truth)
            eval_result = evaluator.metrics()
            print(', '.join(f'{key}: {value}' for key, value in eval_result.items()))
            if eval_metric in ['he', 'lexical']:
                save_results(eval_metric, eval_result, params)
    else:
        online_templates = {k:[v] for k, v in online_templates.items()}
        global_result, oie_remaining = openie_extractor(online_templates, params)
        # Run template based evaluation
        for eval_metric in params['evaluation']:
            get_evaluator = eval_registry.get_eval_metric(eval_metric)
            evaluator = get_evaluator(params)
            remove_varx(global_result)
            remove_varx(ground_truth)
            evaluator.eval(global_result, ground_truth)
            eval_result = evaluator.metrics()
            print(', '.join(f'{key}: {value}' for key, value in eval_result.items()))
            if eval_metric in ['he', 'lexical']:
                save_results(eval_metric, eval_result, params)


if __name__ == "__main__":
    main()
