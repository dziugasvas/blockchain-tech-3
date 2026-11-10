PKG = PKG_CONFIG_PATH=$(HOME)/libbitcoin/lib/pkgconfig pkg-config
LB_CFLAGS = $(patsubst -I%,-isystem%,$(shell $(PKG) --static --cflags libbitcoin-system))
LB_LIBS = $(shell $(PKG) --static --libs libbitcoin-system)
CXXFLAGS = -std=c++11 -O2 -Wall

all: run_merkle

run_merkle: merkle/main.cpp merkle/merkle.cpp merkle/merkle.h
	clang++ $(CXXFLAGS) $(LB_CFLAGS) merkle/main.cpp merkle/merkle.cpp $(LB_LIBS) -o run_merkle

test: merkle/tests.cpp merkle/merkle.cpp merkle/merkle.h
	clang++ $(CXXFLAGS) $(LB_CFLAGS) merkle/tests.cpp merkle/merkle.cpp $(LB_LIBS) -o run_tests && ./run_tests

clean:
	rm -f run_merkle run_tests