#!/usr/bin/python

import sys
import json

from coreTypes import MemorySystem
from coreTypes import RawObject
from misc.utils import text2bytes

class Parser:
    loads_raw_obj = None
    stores_raw_obj = None
    sizes_raw_obj = None
    latencies_raw_obj = None 
    mem_systems = []
    num_ranks = 0
    rank = 0
    rank_stats = None

    def __init__(self, args):
        self.num_ranks = args.num_ranks
        self.rank_stats = args.rank_statistics
        self.rank = args.rank       

        pagesize = text2bytes(args.page)
        self.parseConfig(args.mem_config, pagesize)

        self.loads_raw_obj = RawObject(file_handler=args.loads)
        self.stores_raw_obj = RawObject(file_handler=args.stores)
        self.sizes_raw_obj = RawObject(file_handler=args.sizes, isSize=True)
        
        #if args.lats:
        #    self.latencies_raw_obj = RawObject(args.lats)
        #else:
        self.latencies_raw_obj = RawObject()

    def parseConfig(self, fmem_config_file, pagesize):
        with open(fmem_config_file, 'rU') as fmem_config:
            fmem_config_lines = fmem_config.readlines()

        for line in fmem_config_lines:
            if line[-1] == "\n":
                line = line[:-1]
            fields = line.split(",")
            name = fields[0]
            load_latency = int(fields[1])
            store_latency = int(fields[2])
            size = text2bytes(fields[3])
            if self.rank_stats == 'Average':
                size = size / self.num_ranks
            allocator = fields[4]
            self.mem_systems.append(MemorySystem(name, load_latency, store_latency, size, allocator, pagesize))


    def parse(self, removeZeroSizes=True):
        self.loads_raw_obj.items, self.loads_raw_obj.misses = self.parseInputFile(self.loads_raw_obj.file_handler)
    
        if self.stores_raw_obj.file_handler:
            self.stores_raw_obj.items, self.stores_raw_obj.misses = self.parseInputFile(self.stores_raw_obj.file_handler)
        
        self.sizes_raw_obj.items, self.sizes_raw_obj.sizes = self.parseInputFile(self.sizes_raw_obj.file_handler)
        
        if self.latencies_raw_obj.file_handler:
            self.latencies_raw_obj.items, self.latencies_raw_obj.misses = self.parseInputFile(self.latencies_raw_obj.file_handler)

        if removeZeroSizes:
            self._removeZeroSizes()


    def _removeZeroSizes(self):
        # Remove objects with 0-size
        toremove = []
        for i,itm in enumerate(self.sizes_raw_obj.items):
            if float(self.sizes_raw_obj.sizes[i]) == 0.0:
                toremove.append(i)

        # Remove in reverse order, otherwise indices get corrupted/broken as they move
        for i in reversed(toremove):
            if self.stores_raw_obj.file_handler:
                del self.stores_raw_obj.items[i]
                del self.stores_raw_obj.misses[i]
        #    if self.latencies_file:
        #        del self.items_latencies[i]
        #        del self.latencies[i]
            del self.sizes_raw_obj.items[i]
            del self.sizes_raw_obj.sizes[i]
            del self.loads_raw_obj.items[i]
            del self.loads_raw_obj.misses[i]

        check_equal = False
        if self.stores_raw_obj.file_handler:
            check_equal = ( len(self.loads_raw_obj.items) == len(self.stores_raw_obj.items) == len(self.sizes_raw_obj.items) )
        else:
            check_equal = len(self.loads_raw_obj.items) == len(self.sizes_raw_obj.items)
        if not check_equal:
            raise Exception("Error: Items are not same across loads,stores,sizes")
            

    def parseInputFile(self, inputFile):
        line = inputFile.readline()
        items = line.split("\t")[1:-1]

        # Remove the string decorators from paraver (if needed)
        clean_items = []
        for s in items:
            if (s.find ("[") == -1):
                if s.find ("(") != -1 and s.find (")") > s.find ("("):
                    clean_items.append(s[1+s.find("("):s.find(")")])
                else:
                    clean_items.append(s)
            else:
                clean_items.append(s[1+s.find("["):s.find("]")])

        if self.rank > 0:
            for i in range(self.ranks):
                 line = inputFile.readline()
        else:
            while line != "" and self.rank_stats not in line: 
                line = inputFile.readline()
        if line == "":
            raise Exception("Error, premature EOF ", inputFile, self.num_ranks, self.rank_stats)

        weights = line.split("\t")[1:-1]
        
        if len(items) != len(weights):
            print("Error, length mismatch")
            sys.exit(1)
       
        return clean_items, weights


def parseAllocInfoFile(fname):
    col_parsers = {
        'app': int,
        'proc': int,
        'func': int,
        'alloc_time': int,
        'free_time': int,
        'bytes': int,
        'obj_id': int,
    }

    with open(fname) as infile:
        data = json.load(infile)

    assert 'version' in data and data['version'] == 1

    colnames = data['fields']
    dict_allocs = []
    for a in data['allocs']:
        assert len(a) == len(colnames)
        d = {col: col_parsers.get(col, lambda x: x)(v) for col,v in zip(colnames, a)}
        dict_allocs.append(d)

    data['allocs'] = dict_allocs

    # add a reverse mapping from callstacks to numeric object IDs
    data['callstacks'] = {cs[1+cs.find("["):cs.find("]")]: int(oid) for oid,cs in data['objects'].items()}

    return data

def parseTimeslotsInfoFile(fname):
    with open(fname) as infile:
        data = json.load(infile)

    assert 'version' in data and data['version'] == 1

    field_idx = {}
    assert 'field_idx' not in data
    data['field_idx'] = field_idx
    for i,f in enumerate(data['fields']):
        field_idx[f] = i

    return data

