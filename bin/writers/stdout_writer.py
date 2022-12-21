#!/usr/bin/python

import sys

from core.writer import Writer

class StdoutWriter(Writer):
 
    def write(self, distribution, mem_systems):
        # print output
        for i in range(len(mem_systems)):
            size = 0
            if self.args.verbose:
                print("--", mem_systems[i].name, "-", mem_systems[i].realsize, "bytes --")

            if not self.args.verbose and not self.args.visualizer:
                print("# Memory configuration for", mem_systems[i].name, "with size", mem_systems[i].realsize, "bytes")
                # print("# Memory configuration for", mem_systems[i].name, "with size", mem_systems[i].realsize, "bytes and latency", dram.load_latency/mem_systems[i].load_latency, "times faster than DRAM")

            for mo in distribution[i]:
                if not self.args.verbose:
                    if self.args.visualizer:
                        print(mo.callstack + ';' + str(mo.realsize) + ';' + str(mo.loads))
                    else:
                        print(mo.comment() + mo.callstack + " @ " + mem_systems[i].allocator)
                elif self.args.stores:
                    print(mo.callstack, "-", mo.loads, "loads -", mo.stores, "stores -", mo.realsize, "bytes", " - cost ", str(mo.value))
                else:
                    print(mo.callstack, "-", mo.loads, "loads -", mo.realsize, "bytes", " - cost ", str(mo.value))
                size += mo.realsize
            if self.args.verbose:
                print("--")
                if not self.args.stores:
                    print(len(distribution[i]), "objects;", size, "bytes (" + str(size*100./mem_systems[i].realsize) + "%);")
                else:
                    print(len(distribution[i]), "objects;", size, "bytes (" + str(size*100./mem_systems[i].realsize) + "%);")
                print


        if not self.args.verbose: sys.exit(0)

        print("-- WHEREVER --")
        size = 0
        for mo in useless:
            if self.args.stores:
                print(mo.callstack, "-", mo.loads, "loads -", mo.stores, "stores -", mo.realsize, "bytes")
            else:
                print(mo.callstack, "-", mo.loads, "loads -", mo.realsize, "bytes")
            size += mo.realsize
        print("--")
        print(len(useless), "objects;", size, "bytes")


    def print_distribution(distribution, mem_systems, bytes):
        for j in range(len(mem_systems)):
            print("System: ",j, " Objects: ",len(distribution[j]))
            for item in distribution[j]:
                print("Id: ",item.id, " Loads: ",item.loads, " Stores: ",item.stores, " Cost:", item.value)
            print("Occupancy: ", bytes[j] * 100 / mem_systems[j].realsize)


