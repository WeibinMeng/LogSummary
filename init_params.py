import os
import argparse
from uuid import uuid4
import sys


def init_main_args():
    """Init command line args used for configuration."""

    parser = argparse.ArgumentParser(
        description="Runs information extraction from logs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--templates",
        metavar="templates",
        type=str,
        nargs=1,
        help="input raw templates file path",
    )    
    parser.add_argument(
        "--raw_logs",
        metavar="raw_logs",
        type=str,
        nargs=1,
        help="input raw raw_logs file path",
    )
    base_dir_default = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "output"
    )
    parser.add_argument(
        "--base_dir",
        metavar="base_dir",
        type=str,
        nargs=1,
        default=[base_dir_default],
        help="base output directory for output files",
    )
    parser.add_argument(
        "--log_type",
        metavar="log_type",
        type=str,
        nargs=1,
        default=["original"],
        choices=[
            "original",
            "hpc",
            "bgl",
            "hdfs",
            "proxifier",
            ],
        help="Input type of templates.",
    )
    parser.add_argument(
        "--rules",
        metavar="rules",
        type=str,
        nargs=1,
        choices=["team", "new"],
        help="Predefined rules to extract triples from templates.",
    )
    parser.add_argument(
        "--evaluation",
        metavar="evaluation",
        type=str,
        nargs='+',
        default=[],
        choices=["he",
                 "redundancy",
                 "counts",
                 "lexical",
                 ],
        help="Triples extraction evaluation metrics.",
    )
    parser.add_argument(
        "--openie",
        metavar="openie",
        type=str,
        nargs=1,
        default=["stanford"],
        choices=["stanford", "openie5", "ollie", "predpatt", "clausie", "props",],
        help="OpenIE approach to be used for triple extraction.",
    )
    parser.add_argument(
        "--id",
        metavar="id",
        type=str,
        nargs=1,
        help="Experiment id. Automatically generated if not specified.",
    )
    parser.add_argument(
        "--tag",
        action="store_true",
        default=False,
        help="Tag variables in the output triples (i.e. [([variable])] ).",
    )
    parser.add_argument(
        "--save_output",
        action="store_true",
        default=False,
        help="Save the output of logs or templates triples.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="Force overwriting previous output with same id.",
    )

    return parser


def parse_main_args(args):
    """Parse provided args for runtime configuration."""
    params = {
        "evaluation": args.evaluation,
        "base_dir": args.base_dir[0],
        "log_type": args.log_type[0],
        "openie": args.openie[0],
        "tag": args.tag,
        "save_output": args.save_output,
        "force": args.force,
    }
    if args.rules:
        params["rules"] = args.rules[0]
    if args.templates:
        params["templates"] = os.path.normpath(args.templates[0])
    if args.raw_logs:
        params["raw_logs"] = os.path.normpath(args.raw_logs[0])   
    if args.id:
        params['id'] = args.id[0]
    else:
        params['id'] = str(uuid4().time_low)
    print(f"\nExperiment ID: {params['id']}")
    # Creating experiments results folder with the format
    # {experiment_module_name}_{log_type}_{id}
    experiment_name = os.path.basename(sys.argv[0]).split('.')[0]
    params['id_dir'] = os.path.join(
            params['base_dir'],
            '_'.join((
                experiment_name, params['log_type'], params['id']
                ))
        )
    params['results_dir'] = os.path.join(params['id_dir'], "results")

    return params
