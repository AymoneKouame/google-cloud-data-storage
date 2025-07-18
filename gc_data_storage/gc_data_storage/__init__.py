# _init_ for GCPDataStorage, updated 7/18/2025

from gc_data_storage.gc_data_storage import GCPDataStorage

import subprocess
import os

dependencies =  ('google.cloud', 'google.api_core', 'ipython', 'pyarrow', 'openpyxl', 'pandas')

missing_dependencies = []

for dependency in dependencies:
    try:
        __import__(dependency.replace('ipython','IPython'))
        
    except ImportError as e:
        print(e)
        print(f"Installing '{dependency}'.")
        res = subprocess.run(['pip', 'install', '--upgrade', dependency], capture_output=True) 
        
    except ImportError as e:
        missing_dependencies.append(f"{dependency}: {e}")

if missing_dependencies:
    raise ImportError(
        "Unable to import required dependencies:\n" + "\n".join(missing_dependencies)
        +".\nPease install module(s) before proceeding."
    )