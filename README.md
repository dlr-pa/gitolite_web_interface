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
