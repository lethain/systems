activate:
	source ./env/bin/activate

env:
	python3 -m venv ./env

test:
	python3 -m unittest test_*.py

clean:
	rm *~ *.pyc
