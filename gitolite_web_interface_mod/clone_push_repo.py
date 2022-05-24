"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import os
import subprocess

def clone_admin_repo(tmpdir, gitolite_home, gitolite_admin_repo, user):
    new_env = os.environ.copy()
    new_env["HOME"] = gitolite_home
    admin_repo_name = os.path.splitext(
        os.path.split(gitolite_admin_repo)[1])[0]
    git_cmd = 'git clone ' + os.path.join(gitolite_home,
                                          gitolite_admin_repo)
    subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=tmpdir, timeout=3, check=True,
        env=new_env)
    git_cmd = 'git config user.name "' + user + '"'
    subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
        timeout=3, check=True, env=new_env)
    git_cmd = 'git config user.email "' + user + '@'
    git_cmd += os.environ.get('HTTP_HOST') + '"'
    subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
        timeout=3, check=True, env=new_env)
    conf_path = os.path.join(
        tmpdir, admin_repo_name, 'conf/gitolite.conf')
    with open(conf_path, 'r') as fd:
        gitolite_config = fd.read().splitlines()
    return (conf_path, gitolite_config)



def commit_push_config_to_repo(
        tmpdir, gitolite_home, gitolite_admin_repo, message='updated'):
    content = ''
    new_env = os.environ.copy()
    new_env["HOME"] = gitolite_home
    admin_repo_name = os.path.splitext(
        os.path.split(gitolite_admin_repo)[1])[0]
    git_cmd = 'git add conf/gitolite.conf'
    cpi = subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
        timeout=3, check=True, env=new_env)
    if DEBUG:
        content += '<h3>debug</h3>'
        content += '<pre>'
        content += git_cmd
        content += '</pre>'
        content += '<pre>'
        content += cpi.stdout.decode()
        content += '</pre>'
    git_cmd = 'git commit -m "' + message + '"'
    cpi = subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
        timeout=3, check=True, env=new_env)
    if DEBUG:
        content += '<h3>debug</h3>'
        content += '<pre>'
        content += git_cmd
        content += '</pre>'
        content += '<pre>'
        content += cpi.stdout.decode()
        content += '</pre>'
    git_cmd = 'git push'
    git_cmd = 'pwd;ls;cat .git/config;git push'
    git_cmd = 'gitolite push'
    cpi = subprocess.run(
        git_cmd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, cwd=os.path.join(tmpdir, admin_repo_name),
        timeout=3, check=False, env=new_env)
    if DEBUG:
        content += '<h3>debug</h3>'
        content += '<pre>'
        content += git_cmd
        content += '</pre>'
        content += '<pre>'
        content += cpi.stdout.decode()
        content += '</pre>'
        content += '<pre>'
        content += cpi.stderr.decode()
        content += '</pre>'
    return content
