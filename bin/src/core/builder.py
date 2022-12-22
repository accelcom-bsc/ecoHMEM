from core.core_types import MemoryObject

class Builder:
    max_loads = 0
    max_stores = 0
    totv_loads = 0
    totv_stores = 0
    tot_size = 0
    pagesize = 0

    @classmethod
    def build(cls, loads_raw_obj, stores_raw_obj, sizes_raw_obj):
        objects = []
        ignored = []
        useless = []

        items_loads = loads_raw_obj.items
        weights_loads = loads_raw_obj.misses
        items_sizes = sizes_raw_obj.items
        weights_sizes = sizes_raw_obj.sizes
        items_stores = stores_raw_obj.items
        weights_stores = stores_raw_obj.misses

        # build object store, not assuming items are sorted across loads, stores, sizes
        # i.e. items_loads[i] doesn't necessarily correspond to items_sizes[i]
        # using items in loads data as key across sizes and stores
        for i in range(len(items_loads)):
            callstack = items_loads[i]
            loads = int(float(weights_loads[i]))
            stores = 0
            size = 0
            try:
                idx = items_sizes.index(items_loads[i])
                size = int(float(weights_sizes[idx]))
            except:
                size = 0
            if stores_raw_obj.file_handler:
                try:
                    idx = items_stores.index(items_loads[i])
                    stores = int(float(weights_stores[idx]))
                except:
                    stores = 0
            if not callstack == "Unresolved" and callstack.find("Memory object referenced by sampled address") == -1:
                if (loads > 0 or stores > 0) and size > 0:
                    if loads > cls.max_loads: 
                        cls.max_loads = loads
                    if stores > cls.max_stores: 
                        cls.max_stores = stores
                    cls.totv_loads += loads
                    cls.totv_stores += stores
                    cls.tot_size += size
                    
                    objects.append(MemoryObject(callstack, loads, stores, size, cls.pagesize))
                else:
                    useless.append(MemoryObject(callstack, loads, stores, size, cls.pagesize))
            else:
                ignored.append(MemoryObject(callstack, loads, stores, size, cls.pagesize))

        return objects, ignored, useless

 
