indenter:
	find backend -name "*.html" | xargs djhtml -t 2 -i

autopep8:
	find backend -name "*.py" | xargs autopep8 --max-line-length 120 --in-place

isort:
	isort -m 3 *

up:
	docker-compose up -d

lint: autopep8 isort indenter
