(Drive folders must be shared with the developer.gserviceaccount.com address prior)

(Globaleaks must be setup prior as well.  Be sure to add "context_gus" to conf.)

update repos

	sudo apt-get update

make dirs

	mkdir ~/packages
	mkdir ~/conf
	mkdir ~/scripts
	mkdir ~/scripts/py
	mkdir ~/assets
	mkdir ~/assets/sources
	mkdir ~/assets/submissions
	mkdir ~/couchdb

installed unzip
	
	supdo apt-get install unzip

installed git
	
	sudo apt-get install git
	
create a key for git and install it

installed setuptools
	
	sudo apt-get install python-setuptools

installed drive sdk

	easy_install --upgrade google-api-python-client
	
installed python-gnupg

	easy_install python-gnupg

installed python-fabric

	easy_install fabric

installed beautifusoup4

	easy_install beautifusoup4

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
	
installed maven3

	sudo apt-get install maven openjdk-7-jdk
	sudo vi /etc/environment
	***add
	JAVA_HOME="/usr/lib/jvm/java-7-openjdk-amd64"
	***modify whatever path was
	PATH="$PATH:$JAVA_HOME/bin"

	
build couchdb deps

	sudo apt-get build-dep couchdb
	
download cdb source

	wget http://apache.mirrors.hoobly.com/couchdb/source/1.3.1/apache-couchdb-1.3.1.tar.gz
	tar -zxvf apache-couchdb-1.2.1.tar.gz
	
configure, build, install cdb

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
	
set-up couchdb with users, databases (informa_cam, consolidated)

install geocouch

	cd ~/packages
	git clone -b couchdb1.3.x https://github.com/couchbase/geocouch.git
	cd geocouch
	export COUCH_SRC=/home/ubuntu/packages/apache-couchdb-1.3.1/src/couchdb
	make
	sudo cp ~/packages/geocouch/ebin/* /usr/local/lib/couchdb/erlang/lib/couch-1.3.1/ebin
	sudo cp ~/packages/geocouch/etc/couchdb/default.d/geocouch.ini /usr/local/etc/couchdb/default.d
	sudo cp ~/packages/geocouch/share/www/script/test/* /usr/local/share/couchdb/www/script/test
	
	sudo vi /usr/local/share/couchdb/www/script/couch_tests.js
		***add
		loadTest("spatial.js");
		loadTest("list_spatial.js");
		loadTest("etags_spatial.js");
		loadTest("multiple_spatial_rows.js");
		loadTest("spatial_compaction.js");
		loadTest("spatial_design_docs.js");
		loadTest("spatial_bugfixes.js");
		loadTest("spatial_merging.js");
		loadTest("spatial_offsets.js");
	
	sudo vi /etc/environment
		***add
		ERL_FLAGS="-pa /home/ubuntu/packages/geocouch/ebin"
		
install couchdb-lucene
	
	cd ~/packages
	git clone git://github.com/rnewson/couchdb-lucene.git
	cd couchdb-lucene
	mvn
	
	cd target
	unzip couchdb-lucene-0.10.0-SNAPSHOT-dist.zip
	
	sudo vi /usr/local/etc/couchdb/local.ini
	***modify
	[httpd_global_handlers]
	_fti = {couch_httpd_proxy, handle_proxy_req, <<"http://127.0.0.1:5985">>}

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
		
install web stuff

	sudo apt-get install lighttpd
	sudo apt-get install php5-cgi
	sudo apt-get install php5-curl

install python-dev

	sudo apt-get install python-dev
	
make aliases

	vi ~/.bash_aliases
	
	alias cdb='sudo /usr/local/bin/couchdb couchdb'
	alias goto_cdb='screen -r WHATEVER THAT SCREEN IS'
	alias goto_api='screen -r WHATEVER THAT SCREEN IS'
	alias goto_watcher='screen -r WHATEVER THAT SCREEN IS'
	alias lucene='cd /packages/couchdb-lucene/target/couchdb-lucene-0.10.0-SNAPSHOT-dist; ./bin/run'
	alias goto_lucene='screen -r WHATEVER THAT SCREEN IS'
	
upload drive p12 to ~/conf

upload client_secrets.json to ~/conf

symlink ~/conf/conf.py to ~/scripts/py

symlink ~/conf/conf.py to ~/api/	

pull api, j3mifier, and browser from git

compile j3mifier

move api package to wherever, scripts to wherever
