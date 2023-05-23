MODULENAME=apt
NUM_TESTS=3

all: run

run:
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS)

clean:
	rm -f ansible/fuzzed_playbooks/*.yaml
	rm -f specs/*.log
	rm -f specs/*.json