# DatabaseConnector
This module contains the functions for connecting to the database and sending requests. As DBMS supported are PostgreSQL, MariaDB (MySQL) and SQLite. It is used in the MetaCollector and the DatabaseEvaluator.

## Usage
If you want to instantiate this class, you need to have a configuration file (.yaml) or a configuration dict. This file/dict should look like:

```
# PostgreSQL
db_name: imdb
user: postgres
password: postgres
host: localhost
port: 5432
```

for PostgreSQL or like:

```
# MariaDB
database: imdb
user: root
password: maria
host: localhost
port: 3306
```

for MariaDB, respectively with your configuration for the DBMS.

If you want to use SQLite, than you only have to give the path to the db file.

### Examples
PostgreSQL:
```
db_conn = DatabaseConnector(database=Database.POSTGRES)
db_conn.connect(config_file_path="meta_collector/config_postgres.yaml")
```

MariaDB:
```
db_conn = DatabaseConnector(database=Database.MARIADB)
db_conn.connect(config_file_path="meta_collector/config_mariadb.yaml")
```

SQLite:
```
db_conn = DatabaseConnector(database=Database.SQLITE)
db_conn.connect(sqlite_file_path="E:/imdb.db")
```

