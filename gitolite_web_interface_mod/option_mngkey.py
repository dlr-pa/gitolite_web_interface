"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import cgi
import os
import subprocess
import sys

from .output import output

# pylint: disable=missing-docstring


def _option_mngkey_mngkey0(gitolite_wrapper_script, sskm_help_link):
    content = '<h1>manage ssh keys with sskm</h1>\n'
    content += sskm_help_link
    content += '<h2>Your current keys are:</h2>'
    new_env = os.environ.copy()
    new_env["QUERY_STRING"] = "sskm list"
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=False, env=new_env)
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    # create form
    content += '<h2>Your new ssh key:</h2>'
    content += '<p>Paste your public ssh key, which is typically '
    content += 'in the file "~/.ssh/id_ed25519.pub". '
    content += 'Do not provide your private ssh key -- '
    content += 'this would compromise your identity!</p>'
    content += '<p>'
    content += '<form method="POST" action="' + \
        os.environ.get('SCRIPT_NAME') + '?mngkey1">'
    content += '<table>'
    content += '<tr>'
    content += '<td>name (e. g. "@computer"): </td>'
    content += '<td><input type="text" name="name" size="42"></td>'
    content += '</tr><tr>'
    content += \
        '<td>public key (e. g. content of id_ed25519.pub): </td>'
    content += \
        '<td><input type="text" name="pubkey" size="100"></td>'
    content += '</tr>'
    content += '</table>'
    content += '<input type="submit" value="submit"> '
    content += '<input type="reset" value="reset">'
    content += '</p>'
    output(
        title='manage ssh keys with sskm', content=content)
    sys.exit(0)


def _option_mngkey1(
        gitolite_wrapper_script, ssh_gitolite_user, ssh_host, sskm_help_link):
    if ssh_host is None:
        ssh_host = os.environ['HTTP_HOST']
    form = cgi.FieldStorage()
    if ('name' not in form) or ('pubkey' not in form):
        output(
            title='ERROR', content='<p>no post data</p>')
        sys.exit(0)
    new_env = os.environ.copy()
    new_env["QUERY_STRING"] = 'sskm add ' + form["name"].value
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        input=form["pubkey"].value.encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
        timeout=3, check=False, env=new_env)
    content = '<h1>manage ssh keys with sskm (added)</h1>'
    content += sskm_help_link
    content += '<h2>Output:</h2>'
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    content += '<h2>Your ssh keys:</h2>'
    new_env = os.environ.copy()
    new_env["QUERY_STRING"] = "sskm list"
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=False, env=new_env)
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    content += '<h2>Next Step:</h2>'
    content += '<p>Now you have to verify your ssh key (by ssh). '
    content += 'You cannot continue with the web interface.</p>'
    content += '<p>Example:<pre>'
    content += 'ssh -i .ssh/newkey ' + ssh_gitolite_user + '@' + \
        ssh_host + ' sskm confirm-add ' + form["name"].value
    content += '</pre></p>'
    content += '<h2>Cancel:</h2>'
    content += '<p>You can cancel with something like:\n<pre>'
    content += 'ssh ' + ssh_gitolite_user + '@' + ssh_host + \
        ' sskm undo-add ' + form["name"].value
    content += '</pre>\n'
    content += '<a href="' + os.environ.get('SCRIPT_NAME') + \
        '?mngkeysskm undo-add ' + form["name"].value
    content += '">cancel ' + form["name"].value + ' by web</a>'
    content += '</p>'
    output(
        title='manage ssh keys with sskm (added)',
        content=content)
    sys.exit(0)


def _option_mngkey_undo_add(gitolite_wrapper_script, sskm_help_link):
    content = '<h1>manage ssh keys with sskm (' + \
        os.environ['QUERY_STRING'].replace('%20', ' ') + ')</h1>\n'
    content += sskm_help_link
    content += '<h2>Output:</h2>'
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True,
        timeout=3, check=True)
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    content += '<h2>Your current keys are:</h2>'
    new_env = os.environ.copy()
    new_env["QUERY_STRING"] = "sskm list"
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=False, env=new_env)
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    title = os.environ['QUERY_STRING'].replace('%20', ' ')
    output(
        content=content, title=title)
    sys.exit(0)


def option_mngkey(gitolite_wrapper_script, ssh_gitolite_user, ssh_host=None):
    sskm_help_link = '<p>sskm help: <a href="'
    sskm_help_link += 'https://gitolite.com/gitolite/contrib/sskm.html" '
    sskm_help_link += 'target="_blank">'
    sskm_help_link += 'changing keys -- self service key management</a></p>'
    if os.environ['QUERY_STRING'] in ['mngkey', 'mngkey0']:
        _option_mngkey_mngkey0(gitolite_wrapper_script, sskm_help_link)
        # sys.exit(0)
    elif os.environ['QUERY_STRING'] == 'mngkey1':
        _option_mngkey1(
            gitolite_wrapper_script, ssh_gitolite_user, ssh_host,
            sskm_help_link)
        # sys.exit(0)
    elif os.environ['QUERY_STRING'].startswith('mngkeysskm%20undo-add%20'):
        _option_mngkey_undo_add(gitolite_wrapper_script, sskm_help_link)
        # sys.exit(0)
