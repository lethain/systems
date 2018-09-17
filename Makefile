develop:
	./env/bin/python setup.py develop

env:
	python3 -m venv ./env

test:
	python3 -m unittest tests/test_*.py

clean:
	rm *~ *.pyc
