#pragma once

#include <boost/config/warning_disable.hpp>
#include <boost/spirit/home/x3.hpp>
#include <boost/fusion/include/adapt_struct.hpp>
#include <boost/fusion/include/io.hpp>
#include <boost/range/adaptor/map.hpp>

#include <string>
#include <vector>
#include <map>
#include <fstream>
#include <iostream>


namespace pcf {

namespace client { namespace ast
{
    struct option {
        std::string name;
        std::string value;
    };
    struct options {
        std::vector<option> options;
    };

    struct semantic_func {
        std::string level;
        std::string func;
    };
    struct semantic_param {
        std::string level;
        std::string func;
        unsigned param;
        std::string values;
    };
    struct semantics {
        std::vector<semantic_func> funcs;
        std::vector<semantic_param> params;
    };


    struct id_desc {
        unsigned id;
        std::string desc;
    };

    struct states {
        std::vector<id_desc> states;
    };

    struct gradients {
        std::vector<id_desc> gradients;
    };

    struct state_color {
        unsigned state;
        unsigned char red;
        unsigned char green;
        unsigned char blue;
    };
    struct state_colors {
        std::vector<state_color> colors;
    };


    struct gradient_color {
        unsigned gradient;
        unsigned char red;
        unsigned char green;
        unsigned char blue;
    };
    struct gradient_colors {
        std::vector<gradient_color> colors;
    };


    struct event_type {
        unsigned gradient;
        unsigned id;
        std::string desc;
    };
    struct event_value {
        unsigned id;
        std::string desc;
    };

    struct events {
        std::vector<event_type> types;
        std::vector<event_value> values;
    };


    using boost::fusion::operator<<;
}}

} // ns pcf

// We need to tell fusion about our structs to make
// them a first-class fusion citizen. This has to
// be in global scope.


BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::id_desc,
    id, desc
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::states,
    states
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::gradients,
    gradients
)


BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::option,
    name, value
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::options,
    options
)


BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::semantic_func,
    level, func
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::semantic_param,
    level, func, param, values
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::semantics,
    funcs, params
)


BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::state_color,
    state, red, green, blue
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::state_colors,
    colors
)

BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::gradient_color,
    gradient, red, green, blue
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::gradient_colors,
    colors
)

BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::event_type,
    gradient, id, desc
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::event_value,
    id, desc
)
BOOST_FUSION_ADAPT_STRUCT(pcf::client::ast::events,
    types, values
)

namespace pcf
{
namespace client
{
    namespace parser
    {
        namespace x3 = boost::spirit::x3;
        namespace ascii = boost::spirit::x3::ascii;

        using x3::char_;
        using x3::space;
        using x3::ushort_;
        using x3::uint_;
        using x3::ulong_;
        using x3::ulong_long;
        using x3::lit;
        using x3::lexeme;

        // XXX why does spirit not have a ubyte_ parser?
        auto const ubyte_ = x3::uint_parser<unsigned char, 10>{};

        //x3::rule<class options, ast::options> const options = "options";
        x3::rule<class options, std::vector<ast::option>> const options = "options";
        auto const options_def =
            lit("DEFAULT_OPTIONS\n")
            >> lexeme[(+(char_ - space) >> +lit(" ") >> +(char_ - '\n')) % '\n']
            ;
        BOOST_SPIRIT_DEFINE(options);

        x3::rule<class semantics, ast::semantics> const semantics = "semantics";
        auto const semantics_def =
            lit("DEFAULT_SEMANTIC\n")
            >> lexeme[(+(char_ - space) >> +lit(" ") >> +(char_ - '\n')) % '\n']
            // func names can have spaces (e.g. State As Is), is hard to parse the next tokens. By now, assume at least two spaces in separator
            >> -(lexeme[(+(char_ - space) >> +lit(" ") >> +(char_) >> lit(" ") >> +lit(" ") >> uint_ >> +lit(" ") >> +(char_ - space)) % '\n'])
            ;
        BOOST_SPIRIT_DEFINE(semantics);

        //x3::rule<class gradient_colors, ast::gradient_colors> const gradient_colors = "gradient_colors";
        x3::rule<class gradient_colors, std::vector<ast::gradient_color>> const gradient_colors = "gradient_colors";
        auto const gradient_colors_def =
            lit("GRADIENT_COLOR\n")
            >> lexeme[(uint_ >> +lit(" ") >> lit("{") >> ubyte_ >> lit(",") >> ubyte_ >> lit(",") >> ubyte_ >> lit("}")) % '\n']
            ;
        BOOST_SPIRIT_DEFINE(gradient_colors);

        //x3::rule<class gradients, ast::gradients> const gradients = "gradients";
        x3::rule<class gradients, std::vector<ast::id_desc>> const gradients = "gradients";
        auto const gradients_def =
            lit("GRADIENT_NAMES\n")
            >> lexeme[(uint_ >> +lit(" ") >> +(char_ - '\n')) % '\n']
            ;
        BOOST_SPIRIT_DEFINE(gradients);

        //x3::rule<class state_colors, ast::state_colors> const state_colors = "state_colors";
        x3::rule<class state_colors, std::vector<ast::state_color>> const state_colors = "state_colors";
        auto const state_colors_def =
            lit("STATES_COLOR\n")
            >> lexeme[(uint_ >> +lit(" ") >> lit("{") >> ubyte_ >> lit(",") >> ubyte_ >> lit(",") >> ubyte_ >> lit("}")) % '\n']
            ;
        BOOST_SPIRIT_DEFINE(state_colors);

        //x3::rule<class states, ast::states> const states = "states";
        x3::rule<class states, std::vector<ast::id_desc>> const states = "states";
        auto const states_def =
            lit("STATES\n")
            >> lexeme[(uint_ >> +lit(" ") >> +(char_ - '\n')) % '\n']
            ;
        BOOST_SPIRIT_DEFINE(states);

        x3::rule<class events, ast::events> const events = "events";
        auto const events_def =
            lit("EVENT_TYPE\n")
            >> lexeme[(uint_ >> +lit(" ") >> uint_ >> +lit(" ") >> +(char_ - '\n')) % '\n']
            >> -(lit("VALUES\n")
                >> -(lexeme[(uint_ >> +lit(" ") >> +(char_ - '\n')) % '\n']) )
            ;

        BOOST_SPIRIT_DEFINE(events);
    }
}

using client::ast::states;

struct color {
    unsigned char r;
    unsigned char g;
    unsigned char b;
};

struct pcf_reader {
    pcf_reader(std::string fname)
    : fname_(fname) {}

    pcf_reader(pcf_reader&) = delete;

    inline void parse();

    /* options */
    bool has_option(const std::string& name) const {
        auto it = options_.find(name);
        return (it != options_.end());
    }

    std::string option(const std::string& name) const {
        auto it = options_.find(name);
        if (it != options_.end()) {
            return it->second;
        }
        return "";
    }

    auto option_names() const {
        return boost::adaptors::keys(options_);
    }

    /* states */
    bool has_state(unsigned id) const {
        auto it = states_.find(id);
        return (it != states_.end());
    }

    std::string state_desc(unsigned id) const {
        auto it = states_.find(id);
        if (it != states_.end()) {
            return it->second;
        }
        return "";
    }

    auto states() const {
        return boost::adaptors::keys(states_);
    }

    /* state colors */
    bool has_state_color(unsigned id) const {
        auto it = state_colors_.find(id);
        return (it != state_colors_.end());
    }

    color state_color(unsigned id) const {
        auto it = state_colors_.find(id);
        if (it != state_colors_.end()) {
            return it->second;
        }
        return {0,0,0};
    }

    auto state_colors() const {
        return boost::adaptors::keys(state_colors_);
    }

    /* gradients */
    bool has_gradient(unsigned id) const {
        auto it = gradients_.find(id);
        return (it != gradients_.end());
    }

    std::string gradient_desc(unsigned id) const {
        auto it = gradients_.find(id);
        if (it != gradients_.end()) {
            return it->second;
        }
        return "";
    }

    auto gradients() const {
        return boost::adaptors::keys(gradients_);
    }

    /* gradient colors */
    bool has_gradient_color(unsigned id) const {
        auto it = gradient_colors_.find(id);
        return (it != gradient_colors_.end());
    }

    color gradient_color(unsigned id) const {
        auto it = gradient_colors_.find(id);
        if (it != gradient_colors_.end()) {
            return it->second;
        }
        return {0,0,0};
    }

    auto gradient_colors() const {
        return boost::adaptors::keys(gradient_colors_);
    }

    /**/
    inline const std::map<unsigned, std::string>& event_values(unsigned event) {
        auto it = events_.find(event);
        if (it != events_.end()) {
            return it->second;
        }
        return empty;
    }

    inline std::string event_desc(unsigned event) {
        auto it = event_descs_.find(event);
        if (it != event_descs_.end()) {
            return it->second;
        }
        return "";
    }

private:
    std::string fname_;
    std::map<std::string, std::string> options_;

    std::map<unsigned, std::string> states_;
    std::map<unsigned, color> state_colors_;

    std::map<unsigned, std::string> gradients_;
    std::map<unsigned, color> gradient_colors_;

    std::map<unsigned, std::map<unsigned, std::string> > events_;
    std::map<unsigned, std::string> event_descs_;

    const std::map<unsigned, std::string> empty;
};

inline void pcf_reader::parse()
{
    namespace x3 = boost::spirit::x3;

    std::ifstream istm(fname_);
    if (istm.fail()) {
        std::cerr << "Error while opening pcf file '" << fname_ << "'\n";
        exit(1); // FIXME improve error handling
    }

    std::string line;
    std::vector<std::string> lines;
    for (size_t line_num = 1; std::getline(istm, line); line_num++) {
        // remove comments and empty lines
        auto comment_start = line.find("#");
        if (comment_start != std::string::npos) line.erase(comment_start);
        if (! line.empty()) lines.push_back(line);
    }

    // reassemble lines in a string for the multi-line parsers
    std::string str;
    for (auto const& l : lines) str += l + '\n';

    auto iter = str.begin();
    auto enditer = str.end();

    while (iter != enditer) {
        client::ast::states sts;
        client::ast::semantics semas;
        client::ast::state_colors st_colors;
        client::ast::gradients grads;
        client::ast::gradient_colors grad_colors;
        client::ast::events evs;
        client::ast::options opts;

        if ( x3::phrase_parse(iter, enditer, client::parser::states, x3::space, sts) ) {
            for (const auto& [id, desc] : sts.states) {
                states_[id] = desc;
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::options, x3::space, opts) ) {
            for (const auto& [name, value] : opts.options) {
                options_[name] = value;
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::gradients, x3::space, grads) ) {
            for (const auto& [id, desc] : grads.gradients) {
                gradients_[id] = desc;
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::state_colors, x3::space, st_colors) ) {
            for (const auto& [st, r, g, b] : st_colors.colors) {
                state_colors_[st] = {r, g, b};
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::gradient_colors, x3::space, grad_colors) ) {
            for (const auto& [grad, r, g, b] : grad_colors.colors) {
                gradient_colors_[grad] = {r, g, b};
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::events, x3::space, evs) ) {
            for (const auto& [grad, ev_type, type_desc] : evs.types) {
                (void)grad; // avoid unused warning
                event_descs_[ev_type] = type_desc;
                for (const auto& [ev_val, desc] : evs.values) {
                    events_[ev_type][ev_val] = desc;
                }
            }
        } else if ( x3::phrase_parse(iter, enditer, client::parser::semantics, x3::space, semas) ) {
            //std::cerr << "Semantics succeeded\n";
            //std::cerr << "  str size " << str.size() << "\n";
            //std::cerr << "  consumed " << iter - str.begin() << "\n";
            //for (const auto& [level, func] : semas.funcs) {
            //    std::cerr << level << "," << func << "|" << std::endl;
            //}
            //for (const auto& [level, func, param, values] : semas.params) {
            //    std::cerr << level << "," << func << "," << param << "|" << values << "|" << std::endl;
            //}
	    // TODO
        } else {
            std::cerr << "Parsing failed" << std::endl;
            for (int i = 0; i < 100 && iter != enditer; i++, iter++) std::cerr << *iter;
            std::cerr << std::endl;
            break;
        }
    }
}

} // ns pcf
