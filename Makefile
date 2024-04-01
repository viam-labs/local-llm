install:
	rye sync

start:
	rye run local-llm

bundle:
	tar -czf module.tar.gz *.sh src dist

upload:
	viam module upload --version $(version) --platform any module.tar.gz

clean:
	rm -rf module.tar.gz dist

.PHONY: build
build:
	rye build

publish: build bundle upload clean
