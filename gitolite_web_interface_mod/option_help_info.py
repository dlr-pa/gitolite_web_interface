"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import os
import subprocess
import sys

from .output import output

# pylint: disable=missing-docstring


def option_help_info(gitolite_wrapper_script):
    cpi = subprocess.run(
        [gitolite_wrapper_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True, timeout=3, check=False)
    if cpi.returncode:
        content = 'returncode = %i\n' % cpi.returncode
        content += 'stdout:\n'
        content += cpi.stdout.decode()
        content += 'stderr:\n'
        content += cpi.stderr.decode()
        output(
            content=content, title='error')
        sys.exit(0)
    content = '<h1>gitolite command (' + \
        os.environ['QUERY_STRING'] + ')</h1>\n'
    content += '<h2>Output:</h2>'
    content += '<pre>' + cpi.stdout.decode() + '</pre>'
    title = 'gitolite command (' + os.environ['QUERY_STRING'] + ')'
    output(
        content=content, title=title)
    sys.exit(0)
