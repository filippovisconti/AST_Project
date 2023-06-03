MODULENAME=lineinfile
NUM_TESTS=4

all: run

run: clean
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS) -s

debug: clean
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS) -s -v

fuzz:
	rm -f ansible/fuzzed_playbooks/*.yaml
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS)

clean:
	rm -f ansible/fuzzed_playbooks/*.yaml
	rm -f specs/inverse_lock

deep_clean:
	rm -f specs/*.log
	rm -f specs/*.json