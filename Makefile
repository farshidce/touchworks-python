VIRTBINPATH:=venv/bin/
ENVPATH:=venv

all: init flake8 package

clean:
	rm -rf $(VIRTBINPATH)
	rm -rf $(ENVPATH)
	rm -rf build
	rm -rf *.egg-info


virtualenv:
	test -d $(VIRTBINPATH)/activate || virtualenv venv
	chmod +x $(VIRTBINPATH)/activate
	$(VIRTBINPATH)/activate
	$(VIRTBINPATH)/pip install --upgrade pip
	$(VIRTBINPATH)/pip install -Ur requirements.txt

init: virtualenv

flake8:
	$(VIRTBINPATH)/flake8 --max-line-length=100 tests/ touchworks/

tests: flake8
	$(VIRTBINPATH)/nosetests tests/*.py
package:
	$(VIRTBINPATH)/python setup.py build
pypi:
	python setup.py bdist bdist_wininst sdist upload -r pypi

