InformaCam-Service
==================

new start for the InformaCam API, without server stuff, and with pulling from repositories

Setup (on ubuntu):
# let ~ represent wherever you want this root to be
# Drive folders must be shared with the developer.gserviceaccount.com address prior

update repos
	sudo apt-get update
	
mkdir ~/packages
mkdir ~/conf
mkdir ~/scripts
mkdir ~/scripts/py
mkdir ~/assets
mkdir ~/assets/sources
mkdir ~/assets/submissions
mkdir ~/couchdb

install unzip
	sudo apt-get install unzip

installed git
	sudo apt-get install git
	
create a key for git and install it

installed setuptools
	sudo apt-get install python-setuptools

installed drive sdk
	easy_install --upgrade google-api-python-client
	
installed python-gnupg
	easy_install python-gnupg

installed pylockfile
	wget https://pylockfile.googlecode.com/files/lockfile-0.9.1.tar.gz
	tar -xvzf pylockfile
	cd pylockfile
	sudo python setup.py install

installed python-daemon
	wget https://pypi.python.org/packages/source/p/python-daemon/python-daemon-1.6.tar.gz#md5=c774eda27d6c5d80b42037826d29e523
	tar -xvzf python-daemon
	cd python-daemon
	python setup.py install
	
installed java
	sudo apt-get install openjdk-7-jre
	
installed g++
	sudo apt-get install g++
	
installed erlang
	sudo apt-get install erlang-base erlang-dev erlang-eunit erlang-nox
	
installed libmoz
	sudo apt-get install libmozjs185-dev

installed libs
	sudo apt-get install libmozjs-dev libicu-dev libcurl4-gnutls-dev libtool
	
build couchdb deps
	sudo apt-get build-dep couchdb
	
download cdb source
	wget http://apache.mirrors.hoobly.com/couchdb/source/1.3.1/apache-couchdb-1.3.1.tar.gz
	
unzip
	tar -zxvf apache-couchdb-1.2.1.tar.gz
	
configure, build, install
	./configure
	make
	sudo make install

copy all files in cdb to our local
	sudo su
	cd /usr/local/var/lib/couchdb
	mv * ~/couchdb
	ln -s /usr/local/var/lib/couchdb ~/couchdb/
	
add couchdb user
	sudo useradd -d /usr/local/var/lib/couchdb couchdb
	sudo usermod -G couchdb -a 'couchdb'
	sudo chown -R couchdb:couchdb ~/couchdb/
	
set-up couchdb with users, databases
	
install python-couchdb
	wget http://pypi.python.org/packages/2.6/C/CouchDB/CouchDB-0.8-py2.6.egg
	sudo easy_install CouchDB-0.8-py2.6.egg
	
install tornado
	wget https://pypi.python.org/packages/source/t/tornado/tornado-3.1.tar.gz
	tar -zxvf tornado-3.1.tar.gz
	cd tornado-3.1
	python setup.py install
	
	
install ffmpeg dependencies
	sudo apt-get install gcc
	sudo apt-get install build-essential
	sudo apt-get install yasm
	sudo apt-get install pkg-config
	sudo apt-get install libx264-dev

install ffmpeg
	git clone git@github.com:FFmpeg/FFmpeg.git
	./configure
	make
	sudo make install
	
install ffmpeg2theora
	sudo apt-get install ffmpeg2theora
	
have Svet install the j3mparser :)
	
install web stuff
	sudo apt-get install lighttpd
	sudo apt-get install php5-cgi
	sudo apt-get install php5-curl
		
upload drive p12 to ~/conf
upload client_secrets.json to ~/conf

symlink ~/conf/conf.py to ~/scripts/py
symlink ~/conf/conf.py to ~/api/

