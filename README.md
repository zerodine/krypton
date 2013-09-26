===================================================
Krypton - HKP GPG Keyserver ``pip install krypton``
===================================================

GPG Keyserver with distribution and Restful interface.


Installation
============

Software
--------

A note for Ubuntu Users. Please read the following article to get m2crypto installed:
http://stackoverflow.com/questions/10553118/problems-installing-m2crypto-on-mint-follow-up

Preparation:
~~~~~~~~~~~~

    apt-get install python-dev # To build PIL
    easy_install -U Sphinx # Only for documentation
    apt-get install swig python-m2crypto # to be able to build the M2Crypto Python Library

Krypton Installation:
~~~~~~~~~~~~~~~~~~~~~

    sudo pip install krypton
    sudo cp /etc/krypton/server.conf.default /etc/krypton/server.conf
    sudo service krypton start

And to update:dd
~~~~~~~~~~~~~~~~

    sudo pip install upgrade krypton

Install directly from source:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    sudo pip install https://github.com/zerodine/krypton/archive/master.zip#egg=krypton

Mongodb
=======

Follow the instructions for your os.

Setup & run
===========

Create two configuration files based on ``server.conf.default``:

 * server.conf
 * (optional to run tests) server.test.conf

Then start the server with the following command.

    python start.py --config server.conf [--port 1234]

===========
Kryptonplus
===========

> !This is part is not OpenSource!

Add the follwoing config into your ``~/.ssh/config`` file to get access to the kryptonplus submodule hosted on bitbucket:

    Host bitbucket-krypton
        HostName bitbucket.org
        User git
        IdentityFile ~/git-deployment/bitbucket-krypton
        IdentitiesOnly yes

The private key for the git deplyomentkey is on confluence in a gpg encrypted form store.
After that, you should be able to update the submodule:

    git submodule init
    git submodule update