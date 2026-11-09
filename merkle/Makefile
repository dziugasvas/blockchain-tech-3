PKG = PKG_CONFIG_PATH=$(HOME)/libbitcoin/lib/pkgconfig pkg-config
LIBBITCOIN = $(shell $(PKG) --static --cflags --libs libbitcoin-system)
CXXFLAGS = -std=c++11 -O2 -Wall -Wno-deprecated-declarations -Wno-deprecated-builtins

all: merkle

merkle: main.cpp merkle.cpp merkle.hpp
	clang++ $(CXXFLAGS) main.cpp merkle.cpp $(LIBBITCOIN) -o merkle

test: tests.cpp merkle.cpp merkle.hpp
	clang++ $(CXXFLAGS) tests.cpp merkle.cpp $(LIBBITCOIN) -o run_tests && ./run_tests

clean:
	rm -f merkle run_tests