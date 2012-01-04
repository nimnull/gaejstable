#!/usr/bin/python

import os
import sys


DIRNAME = os.path.abspath(os.path.dirname(__file__))


sys.path.insert(0,
    os.path.join(DIRNAME, '..', 'var', 'parts', 'google_appengine'))
import dev_appserver
dev_appserver.fix_sys_path()


# Add lib as primary libraries directory, with fallback to lib/dist
# and optionally to lib/dist.zip, loaded using zipimport.
lib_path = os.path.join(DIRNAME, 'lib')
if lib_path not in sys.path:
    sys.path[0:0] = [
        lib_path,
    ]


from flaskext.script import Manager
from flaskext.assets import ManageAssets

from app import app, assets


manager = Manager(app)
manager.add_command("assets", ManageAssets(assets))


if __name__ == '__main__':
    manager.run()
