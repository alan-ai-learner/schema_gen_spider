import sqlite3
from collections import OrderedDict

#Variables
db_schema = {}
db_filename = input("enter path to the sqlite file or name of the file if you are in same directory:--")
sc_keys = ['column_names', 'column_names_original', 'column_types', 'db_id', 'foreign_keys', 'primary_keys', 'table_names', 'table_names_original']


db=sqlite3.connect(db_filename)
db.text_factory = str
cur = db.cursor()

result = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
table_names = list(zip(*result))[0]

def column_json(table_names, col_type):
  columns = [[-1,"*"],]
  if col_type == 'org':
    for i, table_name in enumerate(table_names):
        result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        for j in column_names:
          # print(j.title(), j.lower())
          columns.append([i , j.title()])
          print(columns)
    return columns
  if col_type == 'normal':
    for i, table_name in enumerate(table_names):
        result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        for j in column_names:
          columns.append([i , j.lower()])
    return columns
def columns_datatype(table_names):
   col_data_type = []
   for table_name in table_names:
    data_types = cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
    # foreign_keys = cur.execute(f'PRAGMA foreign_key_list({table_name})').fetchall()
    # print(foreign_keys)
    for i in data_types:
      col_data_type.append(i[2].split('(')[0])  
    for i,j in enumerate(col_data_type):
       if j == 'varchar':
         col_data_type[i] = 'text'
       elif j == 'numeric':
         col_data_type[i] = 'number'
       
   return col_data_type 


#Creating the json,
db_schema = {}
for i in sc_keys:
  if i == 'table_names':
    db_schema["table_names"] = list(table_names)
  elif i == 'table_names_original':
    db_schema["table_names_original"] =  [i.title() for i in list(table_names)]
  elif i == 'column_names':
    db_schema["column_names"] = column_json(table_names,  'normal')
  elif i == 'column_names_original':
    db_schema["column_names_original"] = column_json(table_names, 'org')
  elif i == 'column_types':
    db_schema["column_types"] = columns_datatype(table_names)
  elif i == 'db_id':
    try:
      db_schema["db_id"] = (db_filename.split('/')[-1]).split('.')[0]
    except:
      db_schema["db_id"] = db_filename.split('.')[0]
  elif i == 'foreign_keys':
    db_schema["foreign_keys"] = []
  elif i == 'primary_keys':
    db_schema["primary_keys"] = []

# rearranging the schema

ordered = OrderedDict()
for k in sc_keys:
    ordered[k] = db_schema[k]

# Dumping as json file

import json
with open("demo.json", "w") as outfile:
    json.dump(db_schema, outfile, indent=4)

