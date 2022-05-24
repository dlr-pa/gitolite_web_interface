"""
:Author: Daniel Mohr
:Date: 2022-05-24
"""

import os

def output(title='test page', content='<h1>test</h1>', style=''):
    print('Content-type:text/html\n')
    print('<html>')
    print('<head>')
    print('<title>' + title + '</title>')
    print('<meta http-equiv="Cache-Control" ' +
          'content="no-cache, no-store, must-revalidate"/>')
    print('<meta http-equiv="Pragma" content="no-cache"/>')
    print('<meta http-equiv="Expires" content="0"/>')
    if style:
        print(style)
    print('</head>')
    print('<body>')
    print(content)
    print('<hr>')
    try:
        script_name = os.environ['SCRIPT_NAME']
    except KeyError:
        script_name = '???'
    print('<p align="right"><a href="' + script_name +
          '">back to start</a></p>')
    print('</body>')
    print('</html>')
