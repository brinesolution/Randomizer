install:
	pip install -e .

test:
	pytest -q

web:
	streamlit run apps/web/app.py
