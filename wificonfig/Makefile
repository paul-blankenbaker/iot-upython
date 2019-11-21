pySrcList=$(wildcard src/*.py)
pyDstList=$(pySrcList:src%=dist%)

jsonSrcList=$(wildcard src/*.json)
jsonDstList=$(jsonSrcList:src%=dist%)

htmlSrcList=$(wildcard src/*.html)
htmlDstList=$(htmlSrcList:src%=dist%)

all:	$(htmlDstList) $(jsonDstList) $(pyDstList)

clean:
	rm -fr dist

dist/%.py:	src/%.py
	install -d dist
	sed -e 's,    ,\\t,g' -e '/^\\s*#/d' < $? >| $@;

dist/%.json:	src/%.json
	install -D $? $@

dist/%.html:	src/%.html
	install -D $? $@
