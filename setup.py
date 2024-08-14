import sys  # Добавьте эту строку
from cx_Freeze import setup, Executable

build_options = {
    'packages': [],
    'include_files': ['templates/', 'static/']
}

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('app.py', base=base)
]

setup(name='my_flask_app',
      version='0.1',
      description='My Flask App',
      options={'build_exe': build_options},
      executables=executables)