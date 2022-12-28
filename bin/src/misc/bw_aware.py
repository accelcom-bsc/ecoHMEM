import copy
from core.core_types import MemoryObject

def bw_aware_replacement(distribution, systems, allocs_info):
    debug_bw_centric_allocation = False
    def dbg(*args):
        if debug_bw_centric_allocation:
            print('DEBUG', *args)

    tagged_objects = {}

    for level in range(len(systems)):
        for item in distribution[level]:
            if item.callstack in allocs_info['callstacks']:
                item.id = allocs_info['callstacks'][item.callstack]

        # Items out of advisor
        if level not in tagged_objects:
            tagged_objects[level] = {}
        for item in distribution[level]:
            tagged_objects[level][item.id] = MemoryObject(item.callstack, item.loads, item.stores, item.realsize, item.ecu, item.id, item.value[0])
            dbg(item.id, item.callstack, item.value)

    count = 0
    for e in allocs_info['allocs']:
        found = 0
        for level in range(len(systems)):
            if e['obj_id'] in tagged_objects[level]:
                e['loads'] = tagged_objects[level][e['obj_id']].loads
                e['stores'] = tagged_objects[level][e['obj_id']].stores
                e['callstack'] = tagged_objects[level][e['obj_id']].callstack
                e['level'] = level
                e['value'] = tagged_objects[level][e['obj_id']].value
                found = 1;
                count += 1
                break;

        if found == 0:
            e['loads'] = 0
            e['stores'] =0
            e['callstack'] = 'Unknown'
            e['level'] = 'Unknown'

    obj_instances = {}

    for e in allocs_info['allocs']:
        if e['level'] == 0 or e['level'] == 1:
            if e['obj_id'] not in obj_instances:
               obj_instances[e['obj_id']] = {'total_inst':1, 'inst':1, 'end':e['free_time']}
            else:
                obj_instances[e['obj_id']]['total_inst'] += 1

                if e['alloc_time'] < obj_instances[e['obj_id']]['end']:
                    obj_instances[e['obj_id']]['inst'] += 1
                    obj_instances[e['obj_id']]['end'] = e['free_time']
                else:
                    obj_instances[e['obj_id']]['inst'] = 1
                    obj_instances[e['obj_id']]['end'] = e['free_time']


    dbg("Object instances: ", obj_instances)

    e1 = {}

    new_info = []
    for e in allocs_info['allocs']:
        e['event'] = 1
        e['inst'] = 0
        e['event_time'] = e['alloc_time']
        e['fitting'] = 0
        e['thrashing'] = 0
        e['delta'] = 0
        e['streaming'] = 0
        e['high_bw_alloc'] = 0
        e['dram_bw'] = 0
        e['pmem_bw'] = 0
        e['alive'] = (e['free_time'] - e['alloc_time']) / 10**9
        e['avail'] = {}

        e['loadfreq'] = (float(e['loads']) * 10**12) / (int(e['free_time']) - int(e['alloc_time'])) if e['loads'] else 0
        e['storefreq'] = (float(e['stores']) * 10**12) / (int(e['free_time']) - int(e['alloc_time'])) if e['stores'] else 0

        e1 = e.copy()
        e1['event'] = 0
        e1['event_time'] = e['free_time'];
        e1['ref'] = e

        new_info.append(e1)


    for e in new_info:
        allocs_info['allocs'].append(e)

    dram_size = 0
    pmem_size = 0

    dram_objects = []
    pmem_objects = []

    Th_R    = 100000
    Th_R_L  = 30000
    Th_R_LL = 20000
    Th_R_LH = 50000
    Th_S = 20
    Th_SL = 10
    Th_W = 200
    Th_L = 2

    Th_RWB = Th_S * Th_R
    Th_D_RWB = Th_SL * Th_R

    DRAM_TH=2*1024*1024*1024
    target_objects = []
    replacement_objects = []
    replacement_size = []
    obj_dram_overflow = {}
    obj_dram_all = {}
    obj_pmem_all = {}
    obj_dram_active = {}

    dram_load_bw  = 0
    dram_store_bw = 0
    pmem_load_bw  = 0
    pmem_store_bw = 0

    for e in sorted(allocs_info['allocs'], key=lambda x: x['event_time']):
        cur_time = e['event_time']
        oid = e['obj_id']

        if e['level'] == 0:
            if oid not in obj_dram_all:
                obj_dram_all[oid] = 0
            obj_dram_all[oid] += 1

        if e['level'] == 1:
            if oid not in obj_pmem_all:
                obj_pmem_all[oid] = 0
            obj_pmem_all[oid] += 1

        if e['app'] == 1 and e['proc'] == 1 and e['event'] == 1:
            if e['level'] == 0: # If allocated to DRAM
                dram_size += e['bytes']
                dram_objects.append(e)

                if oid not in obj_dram_active:
                    obj_dram_active[oid] = 0
                obj_dram_active[oid] += 1

                if e['loadfreq']:
                    load_bw = e['loadfreq']
                    dram_load_bw += load_bw

                if e['storefreq']:
                    store_bw = e['storefreq']
                    dram_store_bw += store_bw

                e['dram_bw'] = dram_load_bw
                e['pmem_bw'] = pmem_load_bw

                if e['loadfreq'] >= Th_RWB:
                    e['high_bw_alloc'] = 1

                if int(dram_size) > DRAM_TH and oid not in obj_dram_overflow:
                    obj_dram_overflow[oid] = 1
                    e['fitting'] = 0
                    e['thrashing'] = 1
                else:
                    if oid in obj_dram_overflow:
                        obj_dram_overflow[oid] += 1
                        e['fitting'] = 0
                        e['thrashing'] += 1

                    else:
                        e['fitting'] = 1

                        if oid in obj_instances :
                            if obj_instances[oid]['total_inst'] > Th_L or obj_instances[oid]['inst'] > Th_L:
                                e['streaming'] = 1

            else: # If allocated to PMEM
                if e['level'] != 'Unknown':
                    pmem_size += e['bytes']
                    pmem_objects.append(e)

                if int(dram_size) + int(e['bytes']) > DRAM_TH:
                    e['thrashing'] = 1

                    if dram_size < DRAM_TH:
                        e['delta'] = int(e['bytes']) - (DRAM_TH - dram_size)
                    else:
                        e['delta'] = 0

                if e['loadfreq']:
                    load_bw = e['loadfreq']
                    pmem_load_bw += load_bw

                if e['storefreq']:
                    store_bw = e['storefreq']
                    pmem_store_bw += store_bw

                e['dram_bw'] = dram_load_bw
                e['pmem_bw'] = pmem_load_bw

                if e['loadfreq'] >= Th_D_RWB:
                    e['high_bw_alloc'] = 1

                if oid in obj_instances :
                    if obj_instances[oid]['total_inst'] > Th_L or obj_instances[oid]['inst'] > Th_L:
                        e['streaming'] = 1
        else:
            if e['app'] == 1 and e['proc'] == 1 and e['event'] == 0:
                if e['level'] == 0:
                    dram_size -= e['bytes']

                    if oid in obj_dram_active and obj_dram_active[oid] > 0:
                        obj_dram_active[oid] -= 1

                    if dram_load_bw:
                        dram_load_bw -= e['loadfreq']

                    if dram_store_bw:
                        dram_store_bw -= e['storefreq']
                else:
                    if e['level'] != 'Unknown':
                        pmem_size -= e['bytes']

                    if pmem_load_bw:
                        pmem_load_bw -= e['loadfreq']

                    if pmem_store_bw:
                        pmem_store_bw -= e['storefreq']


        if debug_bw_centric_allocation:
            if (e['loads'] != 0 or e['stores'] != 0) and e['event'] == 1 and e['app'] == 1 and e['proc'] == 1:
                if e['level'] == 0:
                    obj_inst = {}
                    if oid not in obj_inst:
                        obj_inst[oid] = 0
                    obj_inst[oid] += 1

                    print(("A1 Objs:" + str(len(dram_objects)) + " " + str(len(pmem_objects))
                        + " BW:" + str(dram_load_bw) + " " + str(dram_store_bw) + " " + str(pmem_load_bw) + " " + str(pmem_store_bw)
                        + "PID: (" + str(e['app']) +  " " + str(e['proc']) + ") OBJ:" + str(oid) + " INST:(" + str(obj_inst[oid]) + ") "
                        + systems[e['level']].name + " " + str(e['event']) + " " + str(e['event_time']) + " " + str(e['free_time']) + " "
                        + str(e['alive']) + " " + str(e['bytes']) + " " + str(e['loads']) + " " + str(e['stores']) + " " + str(dram_size) + " " + str(pmem_size))
                        + "; Freq: " + str(e['loadfreq']) + " " + str(e['storefreq']) + "{inst:" + str(obj_dram_active[oid]) + " fitting:" + str(e['fitting'])
                        + " thrashing:" + str(e["thrashing"]) + " streaming:" + str(e["streaming"]) + " bandwidth:" + str(e["high_bw_alloc"]) + "}")

                elif e['level'] == 1:
                    print(("B1 Objs:" + " BW:" + str(dram_load_bw) + " " + str(dram_store_bw) + " " + str(pmem_load_bw) + " " + str(pmem_store_bw)
                        + "OBJ:" + str(oid) + " " + systems[e['level']].name + " " + str(e['event']) + " " + str(e['event_time']) + " " + str(e['free_time']) + " "
                        + str(e['alive']) + " " + str(e['bytes']) + " " + str(e['loads']) + " " + str(e['stores']) + " " + str(dram_size) + " " + str(pmem_size))
                        + "; Freq: " + str(e['loadfreq']) + " " + str(e['storefreq']) + "{fitting:" + str(e['fitting']) + " thrashing:" + str(e["thrashing"])
                        + " streaming:" + str(e["streaming"]) + " bandwidth:" + str(e["high_bw_alloc"]) + "}")


    fit_size = 0
    dram_replacement = {}
    pmem_move = {}

    #TODO Take bandwidth calculation into account
    for do in dram_objects:
        oid = do['obj_id']
        if do['fitting'] == 1 and do['pmem_bw'] < Th_R_L:
            if do['bytes'] >= fit_size:
                fit_size = do['bytes']

            if oid not in dram_replacement:
                dram_replacement[oid] = {}
                dram_replacement[oid]['alloc'] = do['event_time']
                dram_replacement[oid]['free']  = do['free_time']
                dram_replacement[oid]['bytes'] = do['bytes']
                dram_replacement[oid]['loads'] = do['loads']
                dram_replacement[oid]['stores'] = do['stores']
                dram_replacement[oid]['total_instances'] = obj_instances[oid]['total_inst']
                dram_replacement[oid]['instances'] = obj_instances[oid]['inst']
                dram_replacement[oid]['avail'] = {}
                dram_replacement[oid]['done'] = False
                dram_replacement[oid]['secondchance'] = False

            if do['streaming'] == 1 and do['high_bw_alloc'] == 1 and do['stores'] == 0:
                if oid not in pmem_move:
                    pmem_move[oid] = 1

    pmem_replacement = {}

    dram_move = {}

    for do in pmem_objects:
        oid = do['obj_id']
        if oid not in pmem_replacement and ((do['thrashing'] == 1 and do['pmem_bw'] > Th_R_L) or (do['loads'] > 0 and do['pmem_bw'] > Th_R) or (do['loads'] > 0 and do['stores'] > 0 and do['pmem_bw'] > Th_R_LL)):
            pmem_replacement[oid] = {}
            pmem_replacement[oid]['alloc'] = do['event_time']
            pmem_replacement[oid]['free']  = do['free_time']
            pmem_replacement[oid]['bytes'] = do['bytes']
            pmem_replacement[oid]['loads'] = do['loads']
            pmem_replacement[oid]['stores'] = do['stores']
            pmem_replacement[oid]['total_instances'] = obj_instances[oid]['total_inst']
            pmem_replacement[oid]['instances'] = obj_instances[oid]['inst']
            pmem_replacement[oid]['delta'] = do['delta']
            pmem_replacement[oid]['avail'] = {}
            pmem_replacement[oid]['done'] = False
            pmem_replacement[oid]['secondchance'] = False
            pmem_replacement[oid]['futuresize'] = 0

        if do['streaming'] == 1 and do['high_bw_alloc'] == 1 and do['stores'] == 0:
            if oid not in dram_move:
                pmem_replacement[oid] = {}
                pmem_replacement[oid]['alloc'] = do['event_time']
                pmem_replacement[oid]['free']  = do['free_time']
                pmem_replacement[oid]['bytes'] = do['bytes']
                pmem_replacement[oid]['loads'] = do['loads']
                pmem_replacement[oid]['stores'] = do['stores']
                pmem_replacement[oid]['total_instances'] = obj_instances[oid]['total_inst']
                pmem_replacement[oid]['instances'] = obj_instances[oid]['inst']
                pmem_replacement[oid]['delta'] = do['delta']
                pmem_replacement[oid]['avail'] = {}
                pmem_replacement[oid]['done'] = False
                pmem_replacement[oid]['secondchance'] = False
                pmem_replacement[oid]['futuresize'] = 0

    # BEGIN DEBUG
    if debug_bw_centric_allocation:
        print(len(dram_objects))
        print(len(pmem_objects))
        print()

        fit_size = 0
        print("These fit in DRAM")
        dram_replacement_debug = {}
        for do in dram_objects:
            oid = do['obj_id']
            if do['fitting'] == 1 and do['pmem_bw'] < Th_R_L:
                if do['bytes'] >= fit_size:
                    fit_size = do['bytes']

                if oid not in dram_replacement_debug:
                    dram_replacement_debug[oid] = {}
                    dram_replacement_debug[oid]['alloc'] = do['event_time']
                    dram_replacement_debug[oid]['free']  = do['free_time']
                    dram_replacement_debug[oid]['bytes'] = do['bytes']
                    dram_replacement_debug[oid]['loads'] = do['loads']
                    dram_replacement_debug[oid]['stores'] = do['stores']
                    dram_replacement_debug[oid]['total_instances'] = obj_instances[oid]['total_inst']
                    dram_replacement_debug[oid]['instances'] = obj_instances[oid]['inst']

        for do in dram_replacement_debug:
            print(do, "SIZE:", dram_replacement_debug[do]['bytes'], "ALLOC:", dram_replacement_debug[do]['alloc'], "FREE:", dram_replacement_debug[do]['free'], "INST:", dram_replacement_debug[do]["instances"], dram_replacement_debug[do]["total_instances"], "LOADS:", dram_replacement_debug[do]['loads'], "STORES:", dram_replacement_debug[do]['stores'])
        #print(dram_replacement)
        print("Fit size", fit_size)
        print("These out of", len(pmem_objects), "goto PMEM")

        pmem_replacement_debug = {}
        for do in pmem_objects:
            oid = do['obj_id']
            if oid not in pmem_replacement_debug and ((do['thrashing'] == 1 and do['pmem_bw'] > Th_R_L) or (do['loads'] > 0 and do['pmem_bw'] > Th_R) or (do['loads'] > 0 and do['stores'] > 0 and do['pmem_bw'] > Th_R_LL)):
                pmem_replacement_debug[oid] = {}
                pmem_replacement_debug[oid]['alloc'] = do['event_time']
                pmem_replacement_debug[oid]['free']  = do['free_time']
                pmem_replacement_debug[oid]['bytes'] = do['bytes']
                pmem_replacement_debug[oid]['loads'] = do['loads']
                pmem_replacement_debug[oid]['stores'] = do['stores']
                pmem_replacement_debug[oid]['pmem_bw'] = do['pmem_bw']
                pmem_replacement_debug[oid]['total_instances'] = obj_instances[oid]['total_inst']
                pmem_replacement_debug[oid]['instances'] = obj_instances[oid]['inst']
                pmem_replacement_debug[oid]['delta'] = do['delta']

            else:
                if oid in pmem_replacement_debug:
                   pmem_replacement_debug[oid]['free'] = do['free_time']

        for do in pmem_replacement_debug:
            print(do, "SIZE:", pmem_replacement_debug[do]['bytes'], "ALLOC:", pmem_replacement_debug[do]['alloc'], "FREE:", pmem_replacement_debug[do]['free'], "INST:", pmem_replacement_debug[do]["instances"], pmem_replacement_debug[do]["total_instances"], "LOADS:", pmem_replacement_debug[do]['loads'], "STORES:", pmem_replacement_debug[do]['stores'], "PMEM BW:", pmem_replacement_debug[do]['pmem_bw'], "DELTA:", pmem_replacement_debug[do]['delta'])

        print()
        print(target_objects)
        print(replacement_objects)
        print(replacement_size)
        print(obj_dram_overflow)
        print(obj_dram_all)
        print(obj_pmem_all)

        print("PMEM Replacement" )
        print(sorted(pmem_replacement, key=lambda x:pmem_replacement[x]['stores'], reverse=True))
        print("DRAM Replacement" )
        print(sorted(dram_replacement, key=lambda x:dram_replacement[x]['stores'], reverse=True))
    # END DEBUG


    # Algo for replacement candidate
    alloc_time_line = []

    for mo in pmem_replacement:
        alloc_time_line.append(pmem_replacement[mo]['alloc'])

    for mo in dram_replacement:
        for time in alloc_time_line:
            if time >= dram_replacement[mo]['alloc'] and time <= dram_replacement[mo]['free']:
                dram_replacement[mo]['avail'][time] = dram_replacement[mo]['bytes']

    avail_dram = {}
    for time in alloc_time_line:
        avail_dram[time] = 0
        for mo in dram_replacement:
            if time in dram_replacement[mo]['avail']:
                avail_dram[time] += dram_replacement[mo]['avail'][time]

    dram_replacement_id = []
    pmem_replacement_id = []
    second_chance_replacement = []

    for pmem_id in sorted(pmem_replacement, key=lambda x:pmem_replacement[x]['stores'], reverse=True):
        dbg(pmem_replacement[pmem_id]['alloc'])

        for dram_id in dram_replacement:
            if dram_replacement[dram_id]['done'] == False and pmem_replacement[pmem_id]['alloc'] in dram_replacement[dram_id]['avail']:
                if dram_replacement[dram_id]['avail'][pmem_replacement[pmem_id]['alloc']] >= pmem_replacement[pmem_id]['bytes']:
                    dbg("Found", dram_id, "for", pmem_id, "allocation size", pmem_replacement[pmem_id]['bytes'])

                    dram_replacement_id.append(dram_id)
                    pmem_replacement_id.append(pmem_id)
                    dram_replacement[dram_id]['done'] = True
                    dram_replacement[dram_id]['avail'][pmem_replacement[pmem_id]['alloc']] -= pmem_replacement[pmem_id]['bytes']
                    dram_replacement[dram_id]['bytes'] -= pmem_replacement[pmem_id]['bytes']
                    break
                else:
                    pmem_replacement[pmem_id]['secondchance'] = True
            else:
                if dram_replacement[dram_id]['done'] == True and dram_replacement[dram_id]['bytes'] > 0:
                    pmem_replacement[pmem_id]['secondchance'] = True
                    pmem_replacement[pmem_id]['delta'] = pmem_replacement[pmem_id]['bytes']


    dbg("DRAM objects available for second chance")

    for pmem_id in sorted(pmem_replacement, key=lambda x:pmem_replacement[x]['stores'], reverse=True):
        if pmem_replacement[pmem_id]['done'] == False and pmem_replacement[pmem_id]['secondchance'] == True and pmem_replacement[pmem_id]['delta'] > 0:
            for dram_id in dram_replacement:
                if pmem_replacement[pmem_id]['alloc'] in dram_replacement[dram_id]['avail'] and dram_replacement[dram_id]['bytes'] > 0:
                    if (dram_replacement[dram_id]['bytes'] * obj_instances[dram_id]['total_inst']) >= pmem_replacement[pmem_id]['delta']:
                        dbg("OBJ:", dram_id, "will be looked for the next chance Pmem size:", pmem_replacement[pmem_id]['delta'], "ID:", pmem_id, "DRAM size", dram_replacement[dram_id]['bytes'] * obj_instances[dram_id]['total_inst'], "bytes")

                        if dram_replacement[dram_id]['bytes'] < pmem_replacement[pmem_id]['delta'] * obj_instances[pmem_id]['total_inst']:
                            dram_replacement[dram_id]['bytes'] = 0
                        else:
                            dram_replacement[dram_id]['bytes'] -= pmem_replacement[pmem_id]['delta']/obj_instances[dram_id]['total_inst']

                        if pmem_id not in second_chance_replacement:
                            pmem_replacement_id.append(pmem_id)

    avail_dram = {}
    for time in alloc_time_line:
        avail_dram[time] = 0
        for mo in dram_replacement:
            if time in dram_replacement[mo]['avail']:
                avail_dram[time] += dram_replacement[mo]['avail'][time]

    # Place objects around DRAM and PMEM
    dram_replaced_obj = []

    dbg(dram_replacement_id)

    for mo in distribution[0]:
        if mo.id in dram_replacement_id:
            dram_replaced_obj.append(mo)

        # If object is to moved to pmem
        if mo.id in pmem_move:
            dram_replaced_obj.append(mo)

    for mo in dram_replaced_obj:
        mo_1 = copy.deepcopy(mo)
        distribution[0].remove(mo)
        distribution[1].append(mo_1)

    pmem_replaced_obj = []

    dbg(pmem_replacement_id)
    dbg(dram_move)

    for mo in distribution[1]:
        if mo.id in pmem_replacement_id:
            pmem_replaced_obj.append(mo)

        # If object is to moved to dram
        if mo.id in dram_move:
            pmem_replaced_obj.append(mo)

    for mo in pmem_replaced_obj:
        mo_1 = copy.deepcopy(mo)

        if mo in distribution[1]:
            distribution[1].remove(mo)
        distribution[0].append(mo_1)


