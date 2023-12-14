#pragma once

#include <boost/config/warning_disable.hpp>
#include <boost/spirit/home/x3.hpp>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/fusion/include/io.hpp>

#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <iostream>
#include <optional>


namespace prv {

namespace client { namespace ast
{
    struct ths_node {
        unsigned num_threads;
        unsigned node;
    };

    struct app_list {
        unsigned num_tasks;
        std::vector<ths_node> threads_per_node;
    };

    struct prv_hdr {
        unsigned short day;
        unsigned short month;
        unsigned short year;
        unsigned short hour;
        unsigned short minute;
        unsigned long total_time;
        std::string time_suffix;
        unsigned num_nodes;
        std::vector<unsigned> cpus_per_node;
        unsigned num_apps;
        std::vector<app_list> apps;
        unsigned num_skip_lines;
    };

    struct type_value {
        unsigned type;
        unsigned long long value;
    };

    struct event {
        unsigned cpu;
        unsigned app;
        unsigned task;
        unsigned thread;
        unsigned long time;
        std::vector<type_value> events;
    };

    struct state {
        unsigned cpu;
        unsigned app;
        unsigned task;
        unsigned thread;
        unsigned long begin;
        unsigned long end;
        unsigned state;
    };

    struct comm_object {
        unsigned cpu;
        unsigned ptask;
        unsigned task;
        unsigned thread;
    };

    struct comm {
        comm_object sender;
        unsigned long psend_time;
        unsigned long lsend_time;
        comm_object receiver;
        unsigned long precv_time;
        unsigned long lrecv_time;
        unsigned size;
        unsigned tag;
    };

    using boost::fusion::operator<<;
}}

} // ns prv

// We need to tell fusion about our structs to make
// them a first-class fusion citizen. This has to
// be in global scope.

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::ths_node,
    num_threads, node
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::app_list,
    num_tasks, threads_per_node
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::prv_hdr,
    day,
    month,
    year,
    hour,
    minute,
    total_time,
    time_suffix,
    num_nodes,
    cpus_per_node,
    num_apps,
    apps,
    num_skip_lines
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::type_value,
    type, value
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::event,
    cpu, app, task, thread, time, events
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::state,
    cpu, app, task, thread, begin, end, state
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::comm_object,
    cpu, ptask, task, thread
)

BOOST_FUSION_ADAPT_STRUCT(prv::client::ast::comm,
    sender, psend_time, lsend_time, receiver, precv_time, lrecv_time, size, tag
)

namespace prv
{

namespace client
{
    namespace parser
    {
        namespace x3 = boost::spirit::x3;
        namespace ascii = boost::spirit::x3::ascii;

        using x3::char_;
        using x3::ushort_;
        using x3::uint_;
        using x3::ulong_;
        using x3::ulong_long;
        using x3::lit;

        auto applist = x3::rule<class app_list, ast::app_list>() =
            uint_
            >> '('
            >> +(uint_ >> ':' >> uint_) % ','
            >> ')'
            ;

        x3::rule<class prv_hdr, ast::prv_hdr> const prv_hdr = "prv_hdr";
        auto const prv_hdr_def =
            lit("#Paraver (")
            >> ushort_ >> '/' >> ushort_ >> '/' >> ushort_
            >> " at "
            >> ushort_ >> ':' >> ushort_ >> "):"
            >> ulong_
            >> *(~char_(':')) >> ':'
            >> uint_
            >> -('(' >> uint_ % ',' >> ")") >> ":"
            >> uint_ >> ':'
            >> applist % ':'
            >> -(',' >> uint_)
            ;

        BOOST_SPIRIT_DEFINE(prv_hdr);

        x3::rule<class event, ast::event> const event = "event";
        auto const event_def =
            lit('2') >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> ulong_ >> ':'
            >> (uint_ >> ':' >> ulong_long) % ':'
            ;

        BOOST_SPIRIT_DEFINE(event);

        x3::rule<class state, ast::state> const state = "state";
        auto const state_def =
            lit('1') >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> uint_ >> ':'
            >> ulong_ >> ':'
            >> ulong_ >> ':'
            >> uint_
            ;

        BOOST_SPIRIT_DEFINE(state);

        x3::rule<class comm, ast::comm> const comm = "comm";
        auto cobj = x3::rule<class comm_object, ast::comm_object>()
            = uint_ >> ':' >> uint_ >> ':' >> uint_ >> ':' >> uint_;

        auto const comm_def =
            lit('3') >> ':'
            >> cobj >> ':'
            >> ulong_ >> ':'
            >> ulong_ >> ':'
            >> cobj >> ':'
            >> ulong_ >> ':'
            >> ulong_ >> ':'
            >> uint_ >> ':'
            >> uint_
            ;

        BOOST_SPIRIT_DEFINE(comm);
    }
}


using client::ast::event;
using client::ast::comm;
using client::ast::state;
using header = client::ast::prv_hdr;

struct listener {
    virtual ~listener() {}
    virtual void handle_header(const header&) {}
    virtual void handle_event(const event&) {}
    virtual void handle_state(const state&) {}
    virtual void handle_comm(const comm&) {}
    virtual void handle_end() {}
};


// This merger expects all events to be time-sorted
struct event_merger_sorted: public listener {
    virtual void handle_header(const header& hdr) {
        for (auto& l : listeners_) l->handle_header(hdr);
    }

    virtual void handle_event(const event& ev) {
        if (cur_time_) {
            if (*cur_time_ == ev.time) {
                client::ast::event* prev = get_prev_event(ev);
                if (prev != nullptr) { // app,task,thread already seen, merge events
                    assert(prev->cpu == ev.cpu);
                    prev->events.insert(prev->events.end(), ev.events.begin(), ev.events.end());
                } else { // app,task,thread not seen for current timestamp, add to list
                    add_prev_event(ev);
                }
            } else {
                assert(*cur_time_ < ev.time);
                // we got a new timestamp -> prev events are complete and can be forwarded
                for (const auto& p : prev_events_) {
                    for (auto& l : listeners_) l->handle_event(p.second);
                }
                // clean up and setup for the new timestamp
                prev_events_.clear();
                cur_time_ = ev.time;
                add_prev_event(ev);
            }
        } else {
            cur_time_ = ev.time;
            add_prev_event(ev);
        }
    }

    virtual void handle_state(const state& st) {
        for (auto& l : listeners_) l->handle_state(st);
    }

    virtual void handle_comm(const comm& com) {
        for (auto& l : listeners_) l->handle_comm(com);
    }

    virtual void handle_end() {
        // flush pending events
        for (const auto& p : prev_events_) {
            for (auto& l : listeners_) l->handle_event(p.second);
        }

        for (auto& l : listeners_) l->handle_end();
    }

    void add_listener(listener* l) {
        listeners_.push_back(l);
    }

private:
    using key_t = unsigned;

    inline key_t make_key(const client::ast::event& ev) {
        constexpr unsigned app_bits = 8;
        constexpr unsigned task_bits = 8;
        constexpr unsigned th_bits = 12;
        static_assert((app_bits + task_bits + th_bits) <= sizeof(key_t)*8);

        constexpr unsigned app_max = (1 << app_bits) - 1;
        constexpr unsigned task_max = (1 << task_bits) - 1;
        constexpr unsigned th_max = (1 << th_bits) - 1;

        assert(ev.app <= app_max);
        assert(ev.task <= task_max);
        assert(ev.thread <= th_max);

        return (ev.app & app_max) << (th_bits + task_bits)
            | (ev.task & task_max) << th_bits
            | (ev.thread & th_max);
    }

    inline void add_prev_event(client::ast::event ev) {
        key_t key = make_key(ev);
        prev_events_[key] = ev;
    }

    inline client::ast::event* get_prev_event(const client::ast::event& ev) {
        key_t key = make_key(ev);
        auto it = prev_events_.find(key);
        if (it == prev_events_.end()) return nullptr;
        else return &(it->second);
    }

    std::optional<unsigned long> cur_time_;
    std::unordered_map<key_t, client::ast::event> prev_events_;

    std::vector<listener*>  listeners_;
};


struct trace_reader {
    trace_reader(std::string fname)
    : fname_(fname) {}

    trace_reader(trace_reader&) = delete;

    inline void parse();

    void add_listener(listener* l) {
        listeners_.push_back(l);
    }

private:
    std::string fname_;
    std::vector<listener*> listeners_;
};

inline void trace_reader::parse()
{
    namespace x3 = boost::spirit::x3;
    typedef std::string::const_iterator iterator_type;

    std::string str;

    std::ifstream istm(fname_);
    if (istm.fail()) {
        std::cerr << "Error while opening prv file '" << fname_ << "'\n";
        exit(1); // FIXME improve error handling
    }

    for (size_t line_num = 1; std::getline(istm, str); line_num++) {
        if (str.empty())
            continue;

        if (str.length() >= 2 && str[0] == 'c' && str[1] == ':')
            continue;

        iterator_type iter = str.begin();
        iterator_type const end = str.end();

        client::ast::prv_hdr hdr;

        if (line_num == 1) {
            if (x3::parse(iter, end, client::parser::prv_hdr, hdr) && iter == end) {
                for (auto& l : listeners_) l->handle_header(hdr);
                continue;
            } else {
                std::cerr << "Header parsing failed, line " << line_num << ": " << str << std::endl;
            }
        }

        client::ast::event ast_ev;
        client::ast::state st;
        client::ast::comm com;

        if (x3::parse(iter, end, client::parser::event, ast_ev) && iter == end) {
            for (auto& l : listeners_) l->handle_event(ast_ev);
        } else if (x3::parse(iter, end, client::parser::state, st) && iter == end) {
            for (auto& l : listeners_) l->handle_state(st);
        } else if (x3::parse(iter, end, client::parser::comm, com) && iter == end) {
            for (auto& l : listeners_) l->handle_comm(com);
        } else {
            std::cerr << "Parsing failed, line " << line_num << ": " << str << std::endl;
        }
    }

    for (auto& l : listeners_) l->handle_end();
}

} // ns prv
