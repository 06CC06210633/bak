 DROP TABLE IF EXISTS sources;
 DROP TABLE IF EXISTS dests;
 DROP TABLE IF EXISTS excludees;
 DROP TABLE IF EXISTS excludee_patterns;
 DROP TABLE IF EXISTS backups;
 DROP TABLE IF EXISTS backup_dests;
 DROP TABLE IF EXISTS backup_sources;

 CREATE TABLE sources(
     id INTEGER PRIMARY KEY,
     path TEXT,
     timestamp  TEXT NOT NULL
 );

 CREATE TABLE dests(
     id INTEGER PRIMARY KEY,
     path TEXT,
     timestamp  TEXT NOT NULL
 );

 CREATE TABLE excludees(
     id INTEGER PRIMARY KEY,
     path TEXT,
     timestamp TEXT NOT NULL
 );

 CREATE TABLE excludee_patterns(
     id INTEGER PRIMARY KEY,
     pattern TEXT NOT NULL,
     timestamp TEXT NOT NULL
 );

 CREATE TABLE backups(
     id INTEGER PRIMARY KEY,
     timestamp TEXT NOT NULL,
     size INTEGER NOT NULL
  );

  CREATE TABLE backup_dests(
      id INTEGER PRIMARY KEY,
      dest INTEGER NOT NULL,
      backup INTEGER NOT NULL, 
      foreign key ("dest") references dests(id),
      foreign key ("backup") references backups(id)
  );
  CREATE TABLE backup_sources(
      id INTEGER PRIMARY KEY,
      source INTEGER NOT NULL,
      backup INTEGER NOT NULL, 
      foreign key ("source") references sources(id),
      foreign key ("backup") references backups(id)
  )
