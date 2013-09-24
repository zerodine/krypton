Krypton - HKP GPG Keyserver
===========================

GPG Keyserver with distribution and Restful interface.

Setup & run
-----------

Create two configuration files based on ``server.conf.default``:

 * server.conf
 * (optional to run tests) server.test.conf

Then start the server with the following command.

    python start.py --config server.conf

Kryptonplus
-----------

Add the follwoing config into your ~/.ssh/config to get access to the submodule:

	Host bitbucket-krypton
		HostName bitbucket.org
		User git
		IdentityFile ~/git-deployment/bitbucket-krypton
		IdentitiesOnly yes