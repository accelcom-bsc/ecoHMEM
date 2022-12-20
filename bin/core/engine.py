#!/usr/bin/python

class Engine:
    objects = []
    mem_systems = []
    algorithm = None
    metric = None
    worst = None

    def __init__(self, objects, mem_systems, algorithm, metric, worst):
        self.objects = objects
        self.mem_systems = mem_systems
        self.algorithm = algorithm
        self.metric = metric
        self.worst = worst 

    def execute(self):
        self.weight_objects()
        distribution = self.distribute()
        return distribution

    def weight_objects(self):
        if self.metric == "misses":
            for item in self.objects:
                item.value = [(item.loads + item.stores) / float(item.size)] * (len(self.mem_systems)-1)
        elif self.metric == "latencies":
            for item in self.objects:
                item.value = [0] * (len(self.mem_systems)-1)
                for i in range(len(self.mem_systems)-1):
                    item.value[i] = (item.loads * self.mem_systems[i+1].load_latency + item.stores * self.mem_systems[i+1].store_latency) / float(item.size)

        if self.algorithm.isdigit():
            tot = 0
            for item in self.objects:
                tot += item.value[0]
            for item in self.objects:
                item.value[0] = item.value[0] * 100 / tot

        # Be bad?
        if self.worst:
            max_value = 0
            for i in range(len(self.mem_systems)-1):
                for item in self.objects:
                    if item.value[i] > max_value: 
                        max_value = item.value[i]
                max_value += 1
                for item in self.objects:
                    item.value[i] = max_value - item.value[i]

    def distribute(self):
        distribution = [None] * len(self.mem_systems)

        new_objects = [obj for obj in self.objects]

        for i in range(len(self.mem_systems)-1):
            if self.algorithm == "precise":
                distribution[i] = self._pack_precise(new_objects, i)
            elif self.algorithm == "greedy":
                distribution[i] = self._pack_greedy(new_objects, i)
            elif self.algorithm.isdigit():
                distribution[i] = self._pack_number(new_objects, i, float(self.algorithm))
            
            new_objects[:] = [item for item in new_objects if item not in distribution[i]]

        size = 0
        for o in new_objects: 
            size += o.size

        if size > self.mem_systems[-1].size:
            raise Exception("Error, doesn't fit")
    
        distribution[-1] = new_objects

        for placement in distribution:
            placement.sort(key=lambda x: x.callstack)

        return distribution

    def _pack_precise(self, items, i):
        def itemSize(item): return item.size
        def itemRealSize(item): return item.realsize

        sizeLimit = self.mem_systems[i].size
        getSize = itemSize
        P = {}
        for nItems in range(len(items)+1):
            for lim in range(sizeLimit+1):
                if nItems == 0:
                    P[nItems, lim] = 0
                elif getSize(items[nItems-1]) > lim:
                    P[nItems, lim] = P[nItems-1,lim]
                else:
                    P[nItems, lim] = max(P[nItems-1,lim],
                                        P[nItems-1,lim-getSize(items[nItems-1])] +
                                        items[nItems-1].value[i])

        L = []
        nItems = len(items)
        lim = sizeLimit
        while nItems > 0:
            nItems -= 1
            if P[nItems+1, lim] != P[nItems,lim]:
                L.append(items[nItems])
                lim -= getSize(items[nItems])

        return L
       
    def _pack_greedy(self, items, i):
        sizeLimit = self.mem_systems[i].size
        items.sort(key=lambda x: x.value[i], reverse = True)
        L = []
        for item in items:
            if item.size <= sizeLimit:
                L.append(item)
                sizeLimit -= item.size
                if sizeLimit == 0: break
        return L
            
    
    def _pack_number(self, items, i, lim):
        sizeLimit = self.mem_systems[i].size
        L = []
    
        for item in items:
            if item.size <= sizeLimit and item.value[i] >= lim:
                print(item.value, lim)
                L.append(item)
                sizeLimit -= item.size
                if sizeLimit == 0: break
        return L
 
