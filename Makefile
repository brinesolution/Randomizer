install:
	pip install -e .

test:
	pytest -q

run-once:
	python scripts/run_once.py

batch:
	python scripts/generate_dataset.py --config config/batch_run.yaml

web:
	streamlit run apps/web/app.py
