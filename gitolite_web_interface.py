#!/usr/bin/env python3
"""
Author: Daniel Mohr.
Date: 2022-05-24 (last change).
License: GNU GENERAL PUBLIC LICENSE, Version 2, June 1991.

[gitolite](https://gitolite.com/gitolite/) is a great tool to manage
[git](https://git-scm.com/) repositories and get access by ssh.

There are also possibilities to use http for transport, e. g.:

  * https://gitolite.com/gitolite/http
  * https://gitolite.com/gitolite/contrib/ssh-and-http

With [sskm](https://gitolite.com/gitolite/contrib/sskm) there is also a tool
available to manage ssh keys for the user over ssh.

But until now there is no possibility to manage ssh keys over http.

Therefore this script *gitolite_web_interface.py* should give the possibility
to add ssh keys over http. After this sskm over ssh can be used to further
manage the keys.

Especially if you have already a directory service (e. g. LDAP)
for managing user accounts with password, this script
*gitolite_web_interface.py* provides the possibility to let the users
manage their ssh keys in a gitolite environment.

To use this script, you have to adapt the following few keys of the global
variable CONFIG:

  * gitolite_wrapper_script
  * ssh_gitolite_user
  * ssh_host
  * only_https
  * gitolite_cmd
  * gitolite_home
  * gitolite_admin_repo
  * creategroup_format
  * provided_options with:
    * help
	* info
	* mngkey
	* creategroup
	* createrepo

You can also overide the CONFIG variable.

More information: https://github.com/dlr-pa/gitolite_web_interface
"""

import gitolite_web_interface_mod

CONFIG = {
    # define the script, which is called when using gitolite over http
    # as described in: https://gitolite.com/gitolite/contrib/ssh-and-http
    'gitolite_wrapper_script': '/var/www/bin/gitolite-suexec-wrapper.sh',
    # define the hosting user of your gitolite installation
    # as described in https://gitolite.com/gitolite/quick_install.html
    'ssh_gitolite_user': 'gitolite',
    # define the ssh host as used in a possible ssh comand;
    # if None, it will be set to HTTP_HOST:
    'ssh_host': None,
    # define if only https traffic is accaptable (True or False):
    'only_https': True,
    # define the gitolite command used on command line
    'gitolite_cmd': 'gitolite',
    # define the gitolite home directory
    'gitolite_home': '/srv/gitolite',
    # define the gitolite admin repository path in the gitolite home
    'gitolite_admin_repo': 'repositories/gitolite-admin.git',
    # define select format of users for creategroup
    # you can choose between 'auto', 'checkbox' and 'select',
    # 'auto' uses 'checkbox' for up to 5 users and 'select' otherwise:
    'creategroup_format': 'auto',
    # define, which options should be provided:
    'provided_options': {
        'help': True,
        'info': True,
        'mngkey': True,
        'creategroup': False,
        'createrepo': False}
}
# start special setting
CONFIG['gitolite_wrapper_script'] = \
    '/srv/www/bin/gitolite-suexec-wrapper.sh'
CONFIG['ssh_gitolite_user'] = 'git'
CONFIG['provided_options'] = {
    'help': True,
    'info': True,
    'mngkey': True,
    'creategroup': False,
    'createrepo': True}
# end special setting


if __name__ == "__main__":
    # call the main program:
    gitolite_web_interface_mod.gitolite_web_interface(
        CONFIG['gitolite_wrapper_script'],
        CONFIG['ssh_gitolite_user'],
        ssh_host=CONFIG['ssh_host'],
        only_https=CONFIG['only_https'],
        gitolite_cmd=CONFIG['gitolite_cmd'],
        gitolite_home=CONFIG['gitolite_home'],
        gitolite_admin_repo=CONFIG['gitolite_admin_repo'],
        provided_options=CONFIG['provided_options'],
        creategroup_format=CONFIG['creategroup_format'])
