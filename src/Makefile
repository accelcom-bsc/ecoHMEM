
CXX ?= g++

BOOST_HOME ?= /usr
BOOST_INC_DIR ?= $(BOOST_HOME)/include

ALL=allocs_info

all: $(ALL)

allocs_info: allocs_info.cpp include/pcf.h include/prv.h include/tuple_hash.h
	$(CXX) $< -o $@ -std=c++17 -O3 -Wall -Wextra -Iinclude -I$(BOOST_INC_DIR)


.PHONY: clean
clean:
	rm -f $(ALL)
