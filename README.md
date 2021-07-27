# README: gitolite web interface

[gitolite](https://gitolite.com/gitolite/) is a great tool to manage
[git](https://git-scm.com/) repositories and get access by
[ssh](https://en.wikipedia.org/wiki/Secure_Shell_Protocol).

There are also possibilities to use
[http](https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol)
for transport, e. g.:

  * [installing on a smart http git server](https://gitolite.com/gitolite/http)
  * [Making repositories available to both ssh and http mode clients](https://gitolite.com/gitolite/contrib/ssh-and-http)

With [sskm](https://gitolite.com/gitolite/contrib/sskm) there is also a tool
available to manage ssh keys for the user over ssh.

But until now there is no possibility to manage ssh keys over http.

Therefore this script [gitolite_web_interface.py](gitolite_web_interface.py)
should give the possibility to add ssh keys over http. After this sskm over
ssh can be used to further manage the keys.

Especially if you have already a directory service (e. g. LDAP)
for managing user accounts with password, this script
*gitolite_web_interface.py* provides the possibility to let the users
manage their ssh keys in a gitolite environment.


## Usage

If you have installed [gitolite](https://gitolite.com/gitolite/) on a server
and enabled http mode 
([Making repositories available to both ssh and http mode clients](https://gitolite.com/gitolite/contrib/ssh-and-http)),
you can use this script:

First you have to enable sskm in gitolite: [changing keys -- self service key management](https://gitolite.com/gitolite/contrib/sskm)

Next you should adapt in *gitolite_web_interface.py* the following few keys of
the global variable CONFIG:

  * gitolite_wrapper_script
  * ssh_gitolite_user
  * ssh_host
  * only_https

Now you can integrate calling it in [apache](https://apache.org/), 
e. g. add the following lines to your apache configuration:

        ScriptAlias /www/ /var/www/bin/gitolite_web_interface.py
        <Location /www>
            AuthType Basic
            AuthName "gitolite access is required"
            Require valid-user
            AuthUserFile /etc/apache2/gitolite.passwd
        </Location>


## copyright + license

Author: Daniel Mohr.

Date: 2021-07-27 (last change).

License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991

Copyright (C) 2021 Daniel Mohr and Deutsches Zentrum fuer Luft- und Raumfahrt e. V., D-51170 Koeln
