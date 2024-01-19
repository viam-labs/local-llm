install:
	./pw install

start:
	./pw start

bundle:
	tar -czf module.tar.gz *.sh src dist

upload:
	viam module upload --version $(version) --platform any module.tar.gz

clean:
	rm module.tar.gz

.PHONY: build
build:
	pdm build

publish: build bundle upload clean
