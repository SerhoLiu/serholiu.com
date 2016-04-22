all: css build

LESSPATH = assets/style/

css:
	lessc $(LESSPATH)effector.less --clean-css="--s1 --advanced" > $(LESSPATH)style.min.css

build: css
	python run.py build

server:
	python run.py server

clean:
	-find . -name '.DS_Store' -exec rm -f {} ';'
	-find . -name '*.py[co]' -exec rm -f {} ';'
