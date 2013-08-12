all: css mincss run

LESSPATH = miniakio/static/style/

css:
	lessc $(LESSPATH)effector.less > $(LESSPATH)style.css

mincss:
	lessc --yui-compress $(LESSPATH)effector.less > $(LESSPATH)style.min.css

run:
	python run.py

clean:
	rm -f $(LESSPATH)style.min.css
	rm -f $(LESSPATH)style.css