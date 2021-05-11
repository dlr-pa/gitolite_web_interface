# README: gitolite web interface

[gitolite](https://gitolite.com/gitolite/) is a great tool to manage git
repositories and get access by ssh.

There are also possibilities to use http for transport, e. g.:

  * [installing on a smart http git server](https://gitolite.com/gitolite/http)
  * [Making repositories available to both ssh and http mode clients](https://gitolite.com/gitolite/contrib/ssh-and-http)

With [sskm](https://gitolite.com/gitolite/contrib/sskm) there is also a tool
available to manage ssh keys for the user over ssh.

But until now there is no possibility to manage ssh keys over http.

Therefore this script *gitolite_web_interface.py* should give the possibility
to add ssh keys over http. After this sskm over ssh can be used to further
manage the keys.

## Using

If you have installed [gitolite](https://gitolite.com/gitolite/) on a server
and enabled http mode 
([Making repositories available to both ssh and http mode clients](https://gitolite.com/gitolite/contrib/ssh-and-http)),
you can use this script:

First you have to enable sskm in gitolite: [changing keys -- self service key management](https://gitolite.com/gitolite/contrib/sskm)

Next you should adapt in *gitolite_web_interface.py* the following few variable
at the last if clause (at the end of the file):

  * gitolite_wrapper_script
  * ssh_gitolite_user
  * ssh_host
  * only_https

Now you can integrate calling it in apache, e. g. add the following lines
to your apache configuration:

		ScriptAlias /www/ /var/www/bin/gitolite_web_interface.py
	    <Location /www>
	        AuthType Basic
	    	AuthName "gitolite access is required"
	    	Require valid-user
	    	AuthUserFile /etc/apache2/gitolite.passwd
	    </Location>


## copyright + license

Author: Daniel Mohr.

Date: 2021-05-11 (last change).

License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991

Copyright (C) 2021 Daniel Mohr
