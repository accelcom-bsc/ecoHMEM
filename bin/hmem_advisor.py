#!/usr/bin/python

import sys
import argparse

from core.coreTypes import *
from core.parser import Parser, parseAllocInfoFile
from core.builder import Builder 
from core.engine import Engine, fit_extra_objects

from writers.file_writer import FileWriter
from writers.stdout_writer import StdoutWriter

from misc.bw_aware import bw_aware_replacement
from misc.utils import text2bytes


def pipeline(args):
    parser = Parser(args)
    parser.parse()
    
    Builder.pagesize = text2bytes(args.page)
    objects, ignored, useless = Builder.build(parser.loads_raw_obj, parser.stores_raw_obj, parser.sizes_raw_obj)

    mem_systems = parser.mem_systems

    engine = Engine(objects, systems, args.algo, args.metric, args.worst)
    distribution = engine.execute()

    if args.allocs_info:
        allocs_info = parseAllocInfoFile(args.allocs_info)
        process = 10
        ca_objs = None
        fit_extra_objects(distribution, mem_systems, allocs_info, 1, process, ca_objs)

        if not args.disable_bw_aware:
            bw_aware_replacement(distribution, mem_systems, allocs_info)

    if args.out:
        writer = FileWriter(args)
    else:
        writer = StdoutWriter(args)
   
    writer.write(distribution, systems)


def main():
    parser = argparse.ArgumentParser(description='hmem_advisor, a memory object distribution tool for heterogeneous memory systems')
    #parser.add_argument('mem_config', type=str)
    #parser.add_argument('accesses_loads', type=argparse.FileType('rU'))
    #parser.add_argument('sizes', type=argparse.FileType('rU'))
    parser.add_argument('--mem-config', type=str, required=True)
    parser.add_argument('--loads', type=argparse.FileType('rU'), required=True)
    parser.add_argument('--sizes', type=argparse.FileType('rU'), required=True)
    parser.add_argument('--stores', type=argparse.FileType('rU'))
    parser.add_argument('--worst', action='store_true', default=False)
    parser.add_argument('--algo', type=str, default='greedy')
    parser.add_argument('--metric', type=str, default='latencies', choices=('latencies','misses'))
    parser.add_argument('--page', type=str, required=False, default="4096b")
    parser.add_argument('--verbose', action='store_true', default=False)
    parser.add_argument('--rank', type=int, default=0)
    parser.add_argument('--rank-statistics', type=str, default="Total")
    parser.add_argument('--visualizer', action='store_true', default=False)
    parser.add_argument('--allocs-info')
    parser.add_argument('--num-ranks', type=int)
    parser.add_argument('--disable-bw-aware', action='store_true', default=False)
    parser.add_argument('--out', type=str)
    args = parser.parse_args()

    # Sanity checks
    if args.algo not in ("greedy", "precise") and not args.algo.isdigit():
        print("Algorithm", args.algo, "not supported")
        sys.exit(1)
    if args.algo.isdigit() and len(systems) > 2:
        print("Algorithm", args.algo, "only supported with 2 memory subsystems;", len(systems), "given")
        sys.exit(1)
    if not args.disable_bw_aware and not args.allocs_info:
        print('The bw-aware placement requires allocs-info data')
        sys.exit(1)
    if args.rank_statistics == 'Average' and not args.num_ranks:
        print('For --rank-statistics=Average you also have to specify --num-ranks')
        sys.exit(1)


    # launch core logic
    pipeline(args)


if __name__ == '__main__':
    main()

