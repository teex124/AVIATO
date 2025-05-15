import subprocess
import sys
import os
import threading

    


def launch_applications():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = current_dir + os.pathsep + env['PYTHONPATH']
    else:
        env['PYTHONPATH'] = current_dir

    main_app = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, 'main.py')],
        env=env
    )
    
    wallet_app = subprocess.Popen(
        [sys.executable, os.path.join(current_dir, 'blockchain', 'pay_main.py')],
        env=env
    )

    
if __name__ == "__main__":
    launch_applications()