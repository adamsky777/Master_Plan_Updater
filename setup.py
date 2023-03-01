from setuptools import setup

APP = ['Master Plan Updater.py']
DATA_FILES = ['keys.json', 'credentials_path_container.yaml', 'downloads_path_container.yaml', 'Master_Plan_links.csv',
              'E-Bikes_Master_Plan_links.csv', 'coll_dep_swap_container.yaml', 'history.html',
              'coll_dep_swap_container.json', 'Temp', 'user_ID.yaml']
OPTIONS = {
 'iconfile': 'cobra.icns',
 'argv_emulation': False,
 'packages': ['certifi']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
