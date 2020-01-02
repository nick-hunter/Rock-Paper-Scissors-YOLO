import os
import sys

def file_path(relative_path):
    if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):
        # running in a PyInstaller bundle
        return os.path.dirname(sys.executable) + "/"  + relative_path
    else:
        #running in a normal Python process
        return os.getcwd() + "/" + relative_path
