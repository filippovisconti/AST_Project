MODULENAME=lineinfile
NUM_TESTS=10

all: run

run: clean
	python3 ./main.py -m $(MODULENAME) -n $(NUM_TESTS)

clean:
	rm -f ansible/fuzzed_playbooks/*.yaml
	rm -f specs/*.log
	rm -f specs/*.json