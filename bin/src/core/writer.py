import sys


def write_result(args, distribution, mem_systems, useless=[]):
    if args.out:
        outFileHandler = open(args.out, 'w')
    else:
        outFileHandler = None

    for i in range(len(mem_systems)):
        size = 0
        if args.verbose:
            print("--", mem_systems[i].name, "-", mem_systems[i].realsize, "bytes --", file=outFileHandler)

        if not args.verbose and not args.visualizer:
            print("# Memory configuration for", mem_systems[i].name, "with size", mem_systems[i].realsize, "bytes", file=outFileHandler)
            # print("# Memory configuration for", mem_systems[i].name, "with size", mem_systems[i].realsize, "bytes and latency", dram.load_latency/mem_systems[i].load_latency, "times faster than DRAM")

        for mo in distribution[i]:
            if not args.verbose:
                if args.visualizer:
                    print(mo.callstack + ';' + str(mo.realsize) + ';' + str(mo.loads), file=outFileHandler)
                else:
                    print(mo.comment() + mo.callstack + " @ " + mem_systems[i].allocator, file=outFileHandler)
            elif args.stores:
                print(mo.callstack, "-", mo.loads, "loads -", mo.stores, "stores -", mo.realsize, "bytes", " - cost ", str(mo.value), file=outFileHandler)
            else:
                print(mo.callstack, "-", mo.loads, "loads -", mo.realsize, "bytes", " - cost ", str(mo.value), file=outFileHandler)
            size += mo.realsize

        if args.verbose:
            print("--", file=outFileHandler)
            if not args.stores:
                print(len(distribution[i]), "objects;", size, "bytes (" + str(size*100./mem_systems[i].realsize) + "%);", file=outFileHandler)
            else:
                print(len(distribution[i]), "objects;", size, "bytes (" + str(size*100./mem_systems[i].realsize) + "%);", file=outFileHandler)
            print(file=outFileHandler)

    if args.verbose:
       print("-- WHEREVER --", file=outFileHandler)
       size = 0
       for mo in useless:
           if args.stores:
               print(mo.callstack, "-", mo.loads, "loads -", mo.stores, "stores -", mo.realsize, "bytes", file=outFileHandler)
           else:
               print(mo.callstack, "-", mo.loads, "loads -", mo.realsize, "bytes", file=outFileHandler)
           size += mo.realsize

       print("--", file=outFileHandler)
       print(len(useless), "objects;", size, "bytes", file=outFileHandler)

    if outFileHandler:
       outFileHandler.close()


