#include <vector>
#include <iterator>
#include <unordered_map>
#include <tuple>
#include <ostream>

#include "prv.h"
#include "pcf.h"
#include "tuple_hash.h"

constexpr int DYNMEM_FUNC_EVENT = 40000040;

constexpr int ALLOC_SIZE_EVENT = 40000041;
constexpr int IN_POINTER_EVENT = 40000042;
constexpr int OUT_POINTER_EVENT = 40000043;
constexpr int ALLOC_OBJECT_EVENT = 32000009;

constexpr int SAMPLED_LOAD_EVENT = 32000000;
constexpr int SAMPLED_STORE_EVENT = 32000001;
constexpr int SAMPLED_OBJECT_EVENT = 32000007;

enum dynmem_func {
    END = 0,
    MALLOC,
    FREE,
    REALLOC,
    CALLOC,
    POSIX_MEMALIGN,
    MEMKIND_MALLOC,
    MEMKIND_CALLOC,
    MEMKIND_REALLOC,
    MEMKIND_POSIX_MEMALIGN,
    MEMKIND_FREE,
    KMPC_MALLOC,
    KMPC_FREE,
    KMPC_REALLOC,
    KMPC_CALLOC,
    KMPC_ALIGNED_MALLOC
};

const char* dynmem_func_name(dynmem_func func) {
    switch(func) {
    case END:
        return "<invalid func>";
    case MALLOC:
        return "malloc";
    case FREE:
        return "free";
    case REALLOC:
        return "realloc";
    case CALLOC:
        return "calloc";
    case POSIX_MEMALIGN:
        return "posix_memalign";
    case MEMKIND_MALLOC:
        return "memkind_malloc";
    case MEMKIND_CALLOC:
        return "memkind_calloc";
    case MEMKIND_REALLOC:
        return "memkind_realloc";
    case MEMKIND_POSIX_MEMALIGN:
        return "memkind_posix_memalign";
    case MEMKIND_FREE:
        return "memkind_free";
    case KMPC_MALLOC:
        return "kmpc_malloc";
    case KMPC_FREE:
        return "kmpc_free";
    case KMPC_REALLOC:
        return "kmpc_realloc";
    case KMPC_CALLOC:
        return "kmpc_calloc";
    case KMPC_ALIGNED_MALLOC:
        return "kmpc_aligned_malloc";
    }
    return "<unknown func>";
}

struct dynmem_ev_t {
    std::optional<dynmem_func> func;
    std::optional<size_t> size;
    std::optional<void*> in_ptr;
    std::optional<void*> out_ptr;
    std::optional<int> object;
};

std::ostream& operator<<(std::ostream& os, const dynmem_ev_t& ad) {
    os << "func:" << ad.func.value_or(dynmem_func(666))
       << " size:" << ad.size.value_or(666)
       << " in:" << ad.in_ptr.value_or((void*)0x666)
       << " out:" << ad.out_ptr.value_or((void*)0x666)
       << " object:" << ad.object.value_or(666)
       ;

    return os;
}

using addr_t = unsigned long;

struct alloc_t {
    size_t bytes;
    addr_t addr;
    dynmem_func alloc_func;
    unsigned long alloc_time;
    unsigned long free_time;
    unsigned alloc_thread;
    unsigned free_thread;
    alloc_t* next_realloc;
    int obj_id;
};

struct dynmem_data_t {
    std::map<addr_t, alloc_t*> live_allocs;
    std::vector<alloc_t*> allocs; // owner
};

std::ostream& warn(const prv::event& e) {
    std::cerr << "WARN <"
        << e.app << ","
        << e.task << ","
        << e.thread << ","
        << e.time << "> ";
    return std::cerr;
}

struct listener: public prv::listener {

    virtual void handle_event(const prv::event& e) {
        assert(prev_time <= e.time);
        prev_time = e.time;

        auto dme = parse_dynmem_ev(e);
        if (dme.func) {
            auto key = std::make_tuple(e.app, e.task);
            auto th_key = std::make_tuple(e.app, e.task, e.thread);
            auto it = pending.find(th_key);
            if (dme.func == END) {
                if (it == pending.end()) warn(e) << "unmatched END func event" << std::endl;
                else {
                    const auto& beg_dme = it->second;
                    switch (*(beg_dme.func)) {
                        case MALLOC:
                        case CALLOC:
                        case POSIX_MEMALIGN: {
                            if (beg_dme.out_ptr) warn(e) << dynmem_func_name(*beg_dme.func) << ": prev already has an out_ptr" << std::endl;

                            if (! dme.out_ptr) warn(e) << dynmem_func_name(*beg_dme.func) << ": end is missing out_ptr" << std::endl;
                            else {
                                alloc_t* palloc = new alloc_t();
                                palloc->bytes = *beg_dme.size;
                                palloc->addr = (addr_t) *dme.out_ptr;
                                palloc->alloc_func = *beg_dme.func;
                                palloc->alloc_time = e.time;
                                palloc->alloc_thread = e.thread;
                                palloc->free_time = 0;
                                palloc->free_thread = 0;
                                palloc->next_realloc = nullptr;

                                if (beg_dme.object) {
                                    palloc->obj_id = *beg_dme.object;
                                } else {
                                    warn(e) << dynmem_func_name(*beg_dme.func) << ": unassigned alloc, size " << palloc->bytes << std::endl;
                                    palloc->obj_id = -1;
                                }

                                dm_data[key].allocs.push_back(palloc);

                                auto la_it = dm_data[key].live_allocs.find(palloc->addr);
                                if (la_it != dm_data[key].live_allocs.end()) warn(e) << dynmem_func_name(*beg_dme.func) << ": already exising address!! " << palloc->addr << std::endl;
                                dm_data[key].live_allocs[palloc->addr] = palloc;
                            }
                            break;
                        }
                        case FREE: {
                            if (! beg_dme.in_ptr) warn(e) << "free missing in_ptr" << std::endl;
                            else {
                                auto la_it = dm_data[key].live_allocs.find((addr_t) *beg_dme.in_ptr);
                                //assert(la_it != dm_data[key].live_allocs.end());
                                if (la_it == dm_data[key].live_allocs.end()) {
                                    warn(e) << "free in_ptr not in live allocs " << *beg_dme.in_ptr << std::endl;
                                } else {
                                    la_it->second->free_time = e.time;
                                    la_it->second->free_thread = e.thread;
                                    dm_data[key].live_allocs.erase(la_it);
                                }
                            }
                            break;
                        }
                        case REALLOC: {
                            alloc_t* in_alloc = nullptr;

                            if (! beg_dme.in_ptr) warn(e) << "realloc missing in_ptr" << std::endl;
                            else {
                                if (*beg_dme.in_ptr != 0) {
                                    auto la_it = dm_data[key].live_allocs.find((addr_t) *beg_dme.in_ptr);
                                    if (la_it == dm_data[key].live_allocs.end()) {
                                        warn(e) << "realloc in_ptr not in live allocs " << *beg_dme.in_ptr << std::endl;
                                    } else {
                                        la_it->second->free_time = e.time;
                                        la_it->second->free_thread = e.thread;

                                        in_alloc = la_it->second;

                                        dm_data[key].live_allocs.erase(la_it);
                                    }
                                }
                            }

                            if (beg_dme.out_ptr) warn(e) << "realloc prev already has an out_ptr" << std::endl;
                            if (! dme.out_ptr) warn(e) << "realloc end is missing out_ptr" << std::endl;
                            else {
                                alloc_t* palloc = new alloc_t();
                                palloc->bytes = *beg_dme.size;
                                palloc->addr = (addr_t) *dme.out_ptr;
                                palloc->alloc_func = *beg_dme.func;
                                palloc->alloc_time = e.time;
                                palloc->alloc_thread = e.thread;
                                palloc->free_time = 0;
                                palloc->free_thread = 0;
                                palloc->next_realloc = nullptr;

                                if (in_alloc) in_alloc->next_realloc = palloc;

                                if (beg_dme.object) {
                                    palloc->obj_id = *beg_dme.object;
                                } else {
                                    warn(e) << "realloc unassigned alloc, size " << palloc->bytes << std::endl;
                                    palloc->obj_id = -1;
                                }

                                dm_data[key].allocs.push_back(palloc);

                                auto la_it = dm_data[key].live_allocs.find(palloc->addr);
                                if (la_it != dm_data[key].live_allocs.end()) warn(e) << "realloc already exising address!! " << palloc->addr << std::endl;
                                dm_data[key].live_allocs[palloc->addr] = palloc;
                            }
                            break;
                        }
                        default:
                            warn(e) << "unhandled func type: " << *(beg_dme.func) << std::endl;
                    }
                    pending.erase(it);
                }
            } else {
                if (it != pending.end()) warn(e) << "func event not ended" << std::endl;
                pending[th_key] = dme;
            }
        }
    }

private:

    dynmem_ev_t parse_dynmem_ev(const prv::event& e) {
        dynmem_ev_t ret;
        for (const auto& tv : e.events) {
            switch (tv.type) {
            case DYNMEM_FUNC_EVENT:
                ret.func = (dynmem_func)tv.value;
                break;
            case ALLOC_SIZE_EVENT:
                ret.size = tv.value;
                break;
            case IN_POINTER_EVENT:
                ret.in_ptr = (void*)tv.value;
                break;
            case OUT_POINTER_EVENT:
                ret.out_ptr = (void*)tv.value;
                break;
            case ALLOC_OBJECT_EVENT:
                ret.object = tv.value;
                break;
            }
        }
        return ret;
    }

    size_t prev_time = 0;

public:
    std::unordered_map<std::tuple<unsigned,unsigned,unsigned>, dynmem_ev_t> pending;
    std::unordered_map<std::tuple<unsigned,unsigned>, dynmem_data_t> dm_data;
};

int main(int argc, char** argv) {

    if (argc != 2) return 1;

    const std::string prv_fname(argv[1]);
    prv::trace_reader r(prv_fname);

    listener l;

    prv::event_merger_sorted emr;
    emr.add_listener(&l);
    r.add_listener(&emr);

    std::cout << "{\n";
    std::cout << "  \"version\": 1,\n";
    int count = prv_fname.size() - 4;
    if (count >= 0) {
        std::string pcf_fname = prv_fname.substr(0, count);
        pcf_fname += ".pcf";
        pcf::pcf_reader pcf_r(pcf_fname);

        pcf_r.parse();

        bool first = true;
        std::cout << "  \"objects\": {\n";
        for (const auto& [id,callstack] : pcf_r.event_values(ALLOC_OBJECT_EVENT)) {
            if (first) first = false;
            else std::cout << ",\n";

            std::cout << "    \"" << id << "\": \"" << callstack << "\"";
        }
        std::cout << "\n  },\n";
    }

    r.parse();

    std::cout << "  \"fields\": [\"app\",\"proc\",\"func\",\"alloc_time\",\"free_time\",\"bytes\",\"obj_id\"],\n";

    bool first = true;
    std::cout << "  \"allocs\": [\n";
    for (const auto& t : l.dm_data) {
        unsigned app = std::get<0>(t.first);
        unsigned task = std::get<1>(t.first);

        std::cerr << app << " " << task << " " << t.second.live_allocs.size() << std::endl;

        const char sep = ',';
        for (const alloc_t* alloc : t.second.allocs) {
            if (first) first = false;
            else std::cout << ",\n";

            std::cout << "["
                      << app << sep
                      << task << sep
                      << alloc->alloc_func << sep
                      << alloc->alloc_time << sep
                      << alloc->free_time << sep
                      << alloc->bytes << sep
                      << alloc->obj_id << "]";
        }
    }
    std::cout << "\n  ]\n";
    std::cout << "}\n";

    std::cerr << "Done" << std::endl;
    return 0;
}


