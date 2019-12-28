#!/usr/bin/python3.8
"check arguments and option and choose function "
import os
import shutil
import sys
import full

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(DIR_PATH, "database.sqlite3")

if os.path.isdir(os.path.join(DIR_PATH, 'temp')):
    shutil.rmtree(os.path.join(DIR_PATH, 'temp'))
    full.create_temp_dir()
else:
    full.create_temp_dir()
if os.path.isfile(DATABASE_PATH) is False:
    full.create_db(os.path.join(DIR_PATH, "schema.sql"))
if (sys.argv[1] == 'add') and (sys.argv[2] == 'source'):
     full.insert_source()
elif (sys.argv[1] == 'add') and (sys.argv[2] == 'dest'):
     full.insert_dest()
#elif (sys.argv[1] == 'add') and (sys.argv[2] == 'excludee'):
#     full.insert_excludee()
elif (sys.argv[1] == 'add') and (sys.argv[2] == 'pattern'):
     full.insert_excludee_pattern()
elif (sys.argv[1] == 'backup') and (sys.argv[2] == 'full'):
         full.backup()
else:
    print("wrong option")
