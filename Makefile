
all: zip

clean:
	-rm -rf build

images: clean
	mkdir -p build/rftg-cheat
	( cd src && \
	  gimp -i --batch-interpreter python-fu-eval \
		-b 'execfile("arrange.py")' \
		-b 'pdb.gimp_quit(1)' )

zip: images
	( cd build/rftg-cheat && \
	  ln -s ../../docs/tiles.csv && \
	  cp -r ../../res/layout/* . )
	find build -name '*.xcf' -delete
	( cd build && \
	  zip -r rftg-cheat.zip rftg-cheat )

