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
table_names_list = list(table_names)
def column_json(table_names, col_type):
  columns = [[-1,"*"],]
  if col_type == 'org':
    for i, table_name in enumerate(table_names):
        result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        for j in column_names:
          columns.append([i , j.title()])
          # print(columns)
    return columns
  if col_type == 'normal':
    for i, table_name in enumerate(table_names):
        result = cur.execute("PRAGMA table_info('%s')" % table_name).fetchall()
        column_names = list(zip(*result))[1]
        for j in column_names:
          columns.append([i , j.lower()])
    return columns
def columns_datatype(table_names):
   col_data_type = ['text',]
   for table_name in table_names:
    data_types = cur.execute(f'PRAGMA TABLE_INFO({table_name})').fetchall()
    for i in data_types:
      col_data_type.append(i[2].split('(')[0])  
    for i,j in enumerate(col_data_type):
       if j == 'varchar':
         col_data_type[i] = 'text'
       elif j in [ 'numeric','INTEGER','int', 'real']:
         col_data_type[i] = 'number'
       else:
        continue

       
   return col_data_type 

def foreign_key_list(table_names):
  table_names_list = list(table_names)
  column_names = column_json(table_names, 'normal')
  foreign_key_1 = []
  foreign_key_2 = []
  foreign_keys_original =[]

  #logic
  for table_name in enumerate(table_names):
    # print(table_name[0], table_name[1])
    foreign_keys = cur.execute('PRAGMA foreign_key_list(%s);' % table_name[1]).fetchall()
    for foreign_key in foreign_keys:
        for i in range(len(column_names)) :
            if column_names[i][0] == table_name[0] and foreign_key[3] == column_names[i][1]:
                foreign_key_1.append(i)
        for i in range(len(column_names)) :
            index = table_names_list.index(foreign_key[2])
            if column_names[i][0] == index and foreign_key[4] == column_names[i][1] :
                foreign_key_2.append(i)

  # rearranging the keys
  for i in range(len(foreign_key_1)):
    foreign_keys_original.append([foreign_key_1[i], foreign_key_2[i]])
  
  return foreign_keys_original

def primary_key_list(table_names):
  primary_key_original = []
  column_name = column_json(table_names, 'normal')

  for table_name in enumerate(table_names):
    # getting primary_key
    key = cur.execute('SELECT l.name FROM pragma_table_info("%s") as l WHERE l.pk = 1;' % table_name[1]).fetchall()
    try:
      primary_key = key[0][0].lower()
    except:
      continue
    for i in range(len(column_name)) :
        # print(column_name[i])
        if column_name[i][0] == table_name[0] and column_name[i][1] == primary_key :
            primary_key_original.append(i)  
  return primary_key_original

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
    db_schema["foreign_keys"] = foreign_key_list(table_names)
  elif i == 'primary_keys':
    db_schema["primary_keys"] = primary_key_list(table_names)

# rearranging the schema

ordered = OrderedDict()
for k in sc_keys:
    ordered[k] = db_schema[k]

# Dumping as json file

import json
with open("demo.json", "w") as outfile:
    json.dump(db_schema, outfile, indent=4)

print(db_schema)
