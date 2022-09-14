
BATS_FILES=$(wildcard *.bats)

all: check

bats-core-1.7.0: | bats-core-1.7.0.tar.gz tweaks.patch
	tar -xzf bats-core-1.7.0.tar.gz
	patch -p1 < tweaks.patch

.PHONY: check
check: $(BATS_FILES) | bats-core-1.7.0 print_args
	bats-core-1.7.0/bin/bats --print-output-on-failure $(BATS_FILES)


