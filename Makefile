run:
	python3 ./main.py

test:
	python3 -m pytest -v --color=yes .

lint:
	python3 -m isort .

cov:
	python3 -m pytest --cov
