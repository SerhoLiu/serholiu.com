all: css run

LESSPATH = miniakio/static/style/

css:
	lessc $(LESSPATH)effector.less > $(LESSPATH)style.css

run:
	python3 run.py

clean:
	-find . -name '.DS_Store' -exec rm -f {} ';'
	-find . -name '*.py[co]' -exec rm -f {} ';'
	-find . -name '__pycache__' | xargs rm -rf {}
