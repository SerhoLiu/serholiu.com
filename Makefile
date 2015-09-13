all: css run

LESSPATH = miniakio/static/style/

mincss:
	lessc $(LESSPATH)effector.less --clean-css="--s1 --advanced" > $(LESSPATH)style.min.css

run:
	python3.4 run.py

clean:
	-find . -name '.DS_Store' -exec rm -f {} ';'
	-find . -name '*.py[co]' -exec rm -f {} ';'
	-find . -name '__pycache__' | xargs rm -rf {}