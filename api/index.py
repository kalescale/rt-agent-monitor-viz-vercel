import sys
import os
import traceback

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from visualizer_functional import server
    
    # This is the WSGI application that Vercel will use
    app = server
    
    # For debugging - you can remove this in production
    print("Successfully loaded Dash app")
    
except Exception as e:
    print(f"Error loading app: {e}")
    traceback.print_exc()
    raise 