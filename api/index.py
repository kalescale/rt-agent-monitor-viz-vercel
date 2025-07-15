import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from visualizer_functional import server

# This is the WSGI application that Vercel will use
app = server 