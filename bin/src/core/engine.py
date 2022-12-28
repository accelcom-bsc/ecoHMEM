import numpy as np

class Engine:

    def __init__(self, mem_systems, algorithm, metric, worst):
        self.mem_systems = mem_systems
        self.algorithm = algorithm
        self.metric = metric
        self.worst = worst

    def distribute_objects(self, objects):
        self.objects = objects
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


def fit_extra_objects(distribution, systems, allocs_info, app, proc, conc_activity_objs):
    def get_obj_id(memobj):
        if memobj.id != -1:
            return memobj.id
        return allocs_info['callstacks'].get(memobj.callstack, -1)

    dram_idx = [i for i,s in enumerate(systems) if s.name == 'DRAM'][0]
    selected_oids = [get_obj_id(o) for o in distribution[dram_idx]]

    num_procs = len(set(a['proc'] for a in allocs_info['allocs']))
    limit = systems[dram_idx].realsize / float(num_procs)

    assert len(selected_oids) == len(set(selected_oids)), "dups in selected_oids"

    # Group allocs (of selected app,proc) by object ID, as (timestamp, bytes delta) pairs
    objs = {}
    for alloc in allocs_info['allocs']:
        if alloc['app'] != app or alloc['proc'] != proc:
            continue
        # discard allocs with invalid free time
        if alloc['free_time'] <= alloc['alloc_time']:
            continue

        obj_deltas = objs.setdefault(alloc['obj_id'], [])

        obj_deltas.append((alloc['alloc_time'], alloc['bytes']))
        obj_deltas.append((alloc['free_time'], -1 * alloc['bytes']))

    # Convert lists of (time, bytes delta) to two numpy arrays, sorted by time
    np_objs = {}
    for obj_id in sorted(objs):
        if obj_id < 0:
            continue

        # merge deltas that have the same timestamp (realloc frees prev and allocates next in the same timestamp)
        deltas = {}
        for time,delta in objs[obj_id]:
            if time not in deltas:
                deltas[time] = 0
            deltas[time] += delta

        sorted_times = list(sorted(deltas.keys()))

        assert obj_id not in np_objs
        np_objs[obj_id] = {}
        np_objs[obj_id]['time'] = np.asarray(sorted_times)
        np_objs[obj_id]['bytes_delta'] = np.asarray([deltas[t] for t in sorted_times])

        # check that byte deltas are balanced
        assert np_objs[obj_id]['bytes_delta'].sum() == 0

    # merge
    merged_time = np.asarray([])
    for o in np_objs.values():
        merged_time = np.union1d(merged_time, o['time'])

    merged_values = np.zeros((len(np_objs), len(merged_time)))

    for i,oid in enumerate(sorted(np_objs.keys())):
        o = np_objs[oid]
        idxs = np.isin(merged_time, o['time']).nonzero()
        merged_values[i][idxs] = o['bytes_delta']

    #

    obj_ids = list(sorted(np_objs.keys()))


    sel_oids_in_objs = [x for x in selected_oids if x in obj_ids]

    idxs_sel_objs = list(sorted(obj_ids.index(x) for x in sel_oids_in_objs))

    stacked_values = np.cumsum(merged_values, axis=1) # turn byte-deltas to actual count, per object

    sel_values = stacked_values[idxs_sel_objs][:]
    total = np.sum(sel_values, axis=0)

    obj_values = {get_obj_id(o): o.value[0] for objs in distribution for o in objs}

    fits = []
    dont_fit = []

    # iterate over remaining objects sorted by descending cost
    sorted_np_objs = list(sorted(np_objs.keys(), key=lambda x: obj_values.get(x, 0.), reverse=True))
    # if we have high concurrent activity objects information, put them first
    if conc_activity_objs is not None:
        sorted_np_objs = [oid for oid in sorted_np_objs if oid in conc_activity_objs] + [oid for oid in sorted_np_objs if oid not in conc_activity_objs]
        assert len(sorted_np_objs) == len(np_objs)
        assert len(sorted_np_objs) == len(set(sorted_np_objs))

    for oid in sorted_np_objs:
        if oid in selected_oids:
            continue
        idx = obj_ids.index(oid)

        new_total = stacked_values[idx] + total
        if new_total.max() <= limit:
            fits.append(oid)
            total = new_total
        else:
            dont_fit.append(oid)

    objs_in_fits = [(memidx, o) for memidx,objs in enumerate(distribution) for o in objs if get_obj_id(o) in fits]
    for memidx,obj in objs_in_fits:
        assert memidx != dram_idx
        distribution[dram_idx].append(obj)
        distribution[memidx].remove(obj)

