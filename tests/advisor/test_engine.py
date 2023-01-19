#!/usr/bin/python

import unittest

from core.core_types import MemorySystem, MemoryObject
from core.engine import Engine


def generate_mem_systems(page_size):
    dram = MemorySystem("DRAM", 1, 1, 5000, "posix", page_size)
    pmem = MemorySystem("PMEM", 1, 1, 5000, "memkind/pmem", page_size)

    return [dram, pmem]

def generate_all_fit_objects(dram, page_size):
    objects = []
    size = 1
    numObjects = dram.size

    # as many objects as dram size, each with one unit of size and value
    for idx in range(numObjects):
        objects.append(MemoryObject("dram{0}".format(idx), 1, 1, size, page_size))
    
    return objects

def generate_50_50_objects(dram, page_size):
    objects = []
    size = 1
    numObjects = dram.size*2

    for idx in range(numObjects):
        if idx < numObjects/2:
           objects.append(MemoryObject("dram{0}".format(idx), 1, 1, size, page_size))
        else:
           objects.append(MemoryObject("pmem{0}".format(idx), 1, 1, size, page_size))

    return objects  

def fake_distribute(objects):
    dram_objs = []
    pmem_objs = []
    
    for obj in objects:
        if "dram" in obj.callstack:
            dram_objs.append(obj)
        elif "pmem" in obj.callstack:
            pmem_objs.append(obj)

    distribution = [dram_objs, pmem_objs]

    for placement in distribution:
        placement.sort(key=lambda x: x.callstack)

    return distribution 

class TestGreedyEngine(unittest.TestCase):
    def setUp(self):
        # different parameters for the subtests
        self.cases = (
            {'info':'Without page size', 'page_size':1},
            {'info':'With page size', 'page_size':4096}
        )

        # create engine object
        algo = "greedy"
        metric = "latencies"
        worst = False
        self.engine = Engine(None, algo, metric, worst)

    def test_all_fit(self):
        """
            Tests all objects fit in DRAM.
        """

        for case in self.cases:
            with self.subTest(case['info']):
                mem_systems = generate_mem_systems(case['page_size'])
                self.engine.mem_systems = mem_systems
                objects = generate_all_fit_objects(mem_systems[0], case['page_size'])
                calculated_dist = self.engine.distribute_objects(objects)
                expected_dist = fake_distribute(objects)
                self.assertEqual(calculated_dist, expected_dist)

    def test_50_50(self):
        """
            Tests 50-50 distribution between DRAM and PMEM.
        """           
        
        for case in self.cases:
            with self.subTest(case['info']):
                mem_systems = generate_mem_systems(case['page_size'])
                self.engine.mem_systems = mem_systems
                objects = generate_50_50_objects(mem_systems[0], case['page_size'])
                calculated_dist = self.engine.distribute_objects(objects)
                expected_dist = fake_distribute(objects)

                for idx in range(len(calculated_dist)):
                    c_dist = calculated_dist[idx]
                    e_dist = expected_dist[idx]
                    self.assertEqual(len(c_dist), len(e_dist))
                    for i in range(len(c_dist)):
                        if c_dist[i] != e_dist[i]:
                            self.assertEqual(c_dist[i], e_dist[i])

if __name__ == "__main__":
    unittest.main()
