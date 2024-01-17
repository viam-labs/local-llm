bundle:
	tar -czf module.tar.gz *.sh src dist

upload:
	viam module upload --version $(version) --platform linux/arm64 module.tar.gz

clean:
	rm module.tar.gz

build:
	pdm build

publish: build bundle upload clean
