import json
from collections import OrderedDict

from core.core_types import MemorySystem
from misc.utils import text2bytes


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

def parseParamedirCSV(inputFile, rank, rank_stats):
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

    if rank > 0:
        for _ in range(rank):
            line = inputFile.readline()
    else:
        while line != "" and rank_stats not in line:
            line = inputFile.readline()

    if line == "":
        raise Exception("Error, premature EOF ", inputFile, rank, rank_stats)

    weights = line.split("\t")[1:-1]

    assert len(items) == len(weights), "Error, length mismatch"

    return OrderedDict(zip(clean_items, weights))


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


def parseConfig(mem_config_file, pagesize, rank_stats, num_ranks):
    with open(mem_config_file, 'r') as mem_config:
        mem_config_lines = mem_config.readlines()

    mem_systems = []
    for line in mem_config_lines:
        if line[-1] == "\n":
            line = line[:-1]
        fields = line.split(",")
        name = fields[0]
        load_latency = int(fields[1])
        store_latency = int(fields[2])
        size = text2bytes(fields[3])
        if rank_stats == 'Average':
            size = size / num_ranks
        allocator = fields[4]
        mem_systems.append(MemorySystem(name, load_latency, store_latency, size, allocator, pagesize))

    return mem_systems
