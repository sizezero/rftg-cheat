
all: zip

clean:
	rm -rf build/*

images: clean
	mkdir build/rftg-cheat
	( cd src && \
	  gimp -i --batch-interpreter python-fu-eval \
		-b 'execfile("arrange.py")' \
		-b 'pdb.gimp_quit(1)' )

zip: images
	( cd build/rftg-cheat && \
	  ln -s ../../doc/tiles.csv &&\
	  ln -s ../../res/layout )
	( cd build && \
	  zip -r rftg-cheat.zip rftg-cheat )

