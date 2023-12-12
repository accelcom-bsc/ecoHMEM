#pragma once

#include <boost/functional/hash.hpp>


namespace meta {
    struct order {
        template <typename... T>
        order(T&&...) {}
    };
}

namespace std {

template<typename... Ts>
struct hash<tuple<Ts...>> {
    typedef tuple<Ts...> argument_type;
    typedef std::size_t result_type;
    result_type operator()(argument_type const& tup) const noexcept {
        return impl(tup, index_sequence_for<Ts...>{});
    }

private:
    template <typename T>
    int combine(result_type& seed, const T& v) const {
        boost::hash_combine(seed, v);
        return 666;
    }

    template <std::size_t... Is>
    result_type impl(argument_type const& tup, index_sequence<Is...>) const {
        result_type seed = 0;
        meta::order{combine(seed, std::get<Is>(tup))..., 0};
        return seed;
    }
};

} // ns std
