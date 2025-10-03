install:
	pip install -r requirements.txt

run:
	python scripts/run_priceradar.py --config configs/example_nyc.yml

test:
	pytest -q
