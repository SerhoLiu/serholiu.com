all: css run

LESSPATH = miniakio/static/style/

css:
	lessc $(LESSPATH)effector.less > $(LESSPATH)style.css

run:
	python3.4 run.py

clean:
	-find . -name '*.py[co]' -exec rm -f {} ';'
	-find . -name '__pycache__' | xargs rm -rf {}