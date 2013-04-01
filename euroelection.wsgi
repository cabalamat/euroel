# euroelection.wsgi

# need this for virtuualenv:
activate_this = '/home/phil/proj/euroelection/venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))


import os
import sys

sys.path.append('/home/phil/proj')
sys.path.append('/home/phil/proj/euroelection')

from main import app as application

#end