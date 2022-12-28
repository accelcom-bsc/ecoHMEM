import math


class RawObject:
    file_handler = None
    items = []
    misses = []
    sizes = []

    def __init__(self, file_handler=None, items=[], weights=[], isSize=False):
        self.file_handler = file_handler
        self.items = items
        if isSize:
            self.sizes = weights
        else:
            self.misses = weights


class MemoryObject:
    def __init__(self, callstack, loads, stores, size, pagesize, ecu=-1, id=-1, value
=-1):
        self.callstack = callstack
        self.loads = loads
        self.stores = stores
        self.realsize = size
        self.size = int(math.ceil(size/float(pagesize)))
        self.ecu = ecu # EVOP specific,
        self.id = id # used as unique object ID
        self.value = value
        self.alloc_time = 0
        self.free_time = 0


    def __str__(self):
        return str(self.ecu) + " " + str(self.loads) + " " + str(self.stores) + " " + str(self.realsize)

    def __eq__(self, other):
        return self.callstack == other.callstack

    def comment(self):
        if self.callstack.find (":") == - 1 and self.callstack.find("!") == -1:
            return "# Static "
        else:
            return ""


class MemorySystem:
    def __init__(self, name, load_latency, store_latency, size, allocator, pagesize):
        self.name = name
        self.load_latency = load_latency
        self.store_latency = store_latency
        self.size = size
        self.realsize = size
        self.size = int(math.ceil(size/float(pagesize)))
        self.allocator = allocator

    def __str__(self):
        return self.name + " " + str(self.load_latency) + " " + str(self.store_latency) + " " + str(self.realsize)

    def __eq__(self, other):
        return self.name == other.name

