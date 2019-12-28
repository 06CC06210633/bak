"""
this script backups path and files and archive them
author: sak
email: sak@mail.com
"""


import sqlite3
import os.path
import sys
import tarfile
import re
import lzma
import shutil


DIR_PATH = os.path.abspath(os.path.dirname(__file__))
TEMP_ARCHIVE = DIR_PATH + '/temp/temp.tar'
TEMP_COMPRESS = TEMP_ARCHIVE + '.xz'
DATABASE_PATH = os.path.join(DIR_PATH, "database.sqlite3")
print(DATABASE_PATH)


def create_temp_dir():
    "create temp folder"
    os.mkdir(os.path.join(DIR_PATH, 'temp'))


def valid_path(path):
    " check if a given path is valid "
    if os.path.isfile(path) or os.path.isdir(path):
        pass
    else:
        print("invalid file or path")
        sys.exit()


def open_db(database):
    " open connection to database file "
    database = sqlite3.connect(database)
    database.row_factory = lambda cursor, row: row[0]
    return database


def create_db(schema):
    " create database if doesn't exists "
    print(DIR_PATH)
    database = open_db(DATABASE_PATH)
    with open(schema, 'r') as file:
        schema = file.read()
        database.executescript(schema)
        database.commit()
        database.close()


def insert_source():
    """ add a source path or file to be backed up """
    database = open_db(DATABASE_PATH)
    path = input("path to be backed up: ")
    valid_path(path)
    sql = """
            INSERT INTO sources
                ('path', 'timestamp')
            VALUES
                (?, strftime('%Y-%m-%d-%H-%M-%S', 'now', 'localtime'))
          """
    database.execute(sql, (path,),)
    database.commit()
    database.close()
    print("added new path")


def insert_dest():
    " add a destination path to be backed into "
    path = input("path of destination: ")
    valid_path(path)
    database = open_db(DATABASE_PATH)
    sql = """
            INSERT INTO dests
                ('path', 'timestamp')
            VALUES
                (?, strftime('%Y-%m-%d-%H-%M-%S', 'now', 'localtime'))
          """
    database.execute(sql, (path,),)
    database.commit()
    database.close()
    print("added new destination")


def insert_excludee_pattern():
    " add an excludee pattern "
    pattern = input("pattern of excludee: ")
    database = open_db(DATABASE_PATH)
    sql = """
        INSERT INTO
            excludee_patterns('pattern', 'timestamp')
        VALUES
            (?, strftime('%Y-%m-%d-%H-%M-%S', 'now', 'localtime'))
         """
    database.execute(sql, (pattern,),)
    database.commit()
    print("added new pattern")


def insert_backup(size, database):
    " add an entry after every backup in database "
    sql = """
            INSERT INTO
                backups('timestamp', 'size')
            VALUES
                (strftime('%Y-%m-%d-%H-%M-%S', 'now', 'localtime'), ?)
         """
    database.execute(sql, (size,),)
    sql = "SELECT last_insert_rowid() FROM backups"
    backup_id = database.execute(sql).fetchone()
    return backup_id


def get_excludee_patterns():
    " get excludee pattern FROM database "
    database = open_db(DATABASE_PATH)
    sql = "SELECT pattern FROM excludee_patterns"
    patterns = database.execute(sql).fetchall()
    return patterns


def check_pattern(tarinfo):
    " check if file name matches any excludee pattern "
    path_matched_pattern = []
    for pattern in get_excludee_patterns():
        if re.search(pattern, tarinfo.name):
            path_matched_pattern.append(tarinfo.name)
    return path_matched_pattern


def filter_excludee(tarinfo):
    " filter and exclude and excludee path "
    if tarinfo.name in check_pattern(tarinfo):
        return None
    return tarinfo


def si_size(size):
    "show given size in bytes as si convention"
    prefixes = [
        (1000 ** 5, 'PB'),
        (1000 ** 4, 'TB'),
        (1000 ** 3, 'GB'),
        (1000 ** 2, 'MB'),
        (1000 ** 1, 'kB'),
        (1000 ** 0, 'B'),
    ]
    for factor, suffix in prefixes:
        if size >= factor:
            break
    amount = int(size/factor)
    return str(amount) + suffix


def archive(sources):
    "archive paths and files into a tar file"
    tar = tarfile.open(TEMP_ARCHIVE, "w")
    for source in sources:
        if source.split(os.path.sep)[-1] == '':
            last_path_name = source.split(os.path.sep)[-2]
        else:
            last_path_name = source.split(os.path.sep)[-1]
        tar.add(source, arcname=last_path_name, filter=filter_excludee)


def compress():
    "compress archived file with lzma package"
    archive_file = open(TEMP_ARCHIVE, 'rb').read()
    with lzma.open(TEMP_COMPRESS, 'w', preset=9) as compress_file:
        compress_file.write(archive_file)


def insert_backup_dests(dests, database, backup_id):
    "insert dests into backup_dest table"
    dest_ids = []
    for dest in dests:
        sql = "SELECT id FROM dests WHERE dests.path='%s'"
        dest_ids.append(database.execute(sql % dest).fetchone())
    for dest_id in dest_ids:
        sql = "INSERT into backup_dests('dest', 'backup') VALUES(?, ?) "
        database.execute(sql, (dest_id, backup_id,),)


def insert_backup_sources(sources, database, backup_id):
    "Insert sources into backup_dest table"
    source_ids = []
    for source in sources:
        sql = "SELECT id FROM sources WHERE sources.path='%s'"
        source_ids.append(database.execute(sql % source).fetchone())
    for source_id in source_ids:
        sql = "INSERT into backup_sources('source', 'backup') VALUES(?, ?) "
        database.execute(sql, (source_id, backup_id,),)


def backup():
    """
    backup sources into tar archive and then tar archive into
    lzma compressed file
    """
    database = open_db(DATABASE_PATH)
    sources = database.execute("SELECT path FROM sources").fetchall()
    dests = database.execute("SELECT path FROM dests").fetchall()
    sql = "SELECT strftime('%Y-%m-%d-%H-%M-%S', 'now', 'localtime')"
    timestamp = database.execute(sql).fetchone()
    for dest in dests:
        archive(sources)
        compress()
    for dest in dests:
        dest_file = os.path.join(dest, timestamp + '.tar.xz')
        shutil.copy2(TEMP_COMPRESS, dest_file)
    size = os.path.getsize(TEMP_COMPRESS)
    backup_id = insert_backup(size, database)
    insert_backup_dests(dests, database, backup_id)
    insert_backup_sources(sources, database, backup_id)
    database.commit()
    database.close()
    print("complete\n backup size {}".format(si_size(size)))
