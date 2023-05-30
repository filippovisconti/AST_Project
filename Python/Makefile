MODULENAME=lineinfile
NUM_TESTS=3

all: run

run: clean
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS) -s

fuzz:
	rm -f ansible/fuzzed_playbooks/*.yaml
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS)

clean:
	rm -f ansible/fuzzed_playbooks/*.yaml

deep_clean:
	rm -f specs/*.log
	rm -f specs/*.json