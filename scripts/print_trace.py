import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.Tasks import TraceGenerator
import argparse

parser = argparse.ArgumentParser(description="Print trace from a Trampoline application.")
parser.add_argument('--trace_path', type=str, default='data/trace.json', help="Register the path to the trace json file")
parser.add_argument('--tpl_path', type=str, default='data/tpl_static_info.json', help="Register the path to the tpl static info json file")
args = parser.parse_args()

generator = TraceGenerator(args.tpl_path, args.trace_path)
generator.printTrace()