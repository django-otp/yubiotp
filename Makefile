.PHONY: all sdist wheel docs sign upload clean


all: clean sdist wheel docs

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

docs:
	$(MAKE) -C docs html zip

sign:
	for f in dist/*.gz dist/*.whl; do \
	    gpg --detach-sign --armor $$f; \
	done

upload:
	twine upload dist/*

clean:
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info
	$(MAKE) -C docs clean
