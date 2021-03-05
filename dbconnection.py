import mysql.connector
import csv

class DBConnection:
  def __init__(self, u, p, h):
    self.cnx = mysql.connector.connect(user=u, password=p, host=h)
    self.cursor = self.cnx.cursor(dictionary=True)

  def create_database(self, name):
    '''Create the database.'''
    try:
      self.cnx.database = name
    except Exception:
      self.cursor.execute(f'CREATE DATABASE {name};')
      self.cnx.database = name

  def create_tables(self, sql_path):
    '''Create database tables from the given SQL file.'''
    with open(sql_path, 'r') as f:
      for _ in self.cursor.execute(f.read(), multi=True): pass
      self.cnx.commit()

  def fill_table(self, file_path, table):
    '''Fill the given table with data from the given csv file.'''
    with open(file_path, newline='') as f:
      keys = f.readline().strip().split(',')
      nr_of_params = ('%s, ' * len(keys)).rstrip(', ')
      keys = ', '.join(map(lambda x: f'`{x}`', keys))
      for row in csv.reader(f):
        row = map(lambda x: None if x == '' else x, row)
        self.cursor.execute(f'INSERT INTO `{table}` ({keys}) VALUES ({nr_of_params});', tuple(row))
      self.cnx.commit()

  def run(self, query, params=tuple()):
    '''Execute a query.'''
    self.cursor.execute(query, params)
  
  def fetch_all(self):
    '''Fetch all results.'''
    return self.cursor.fetchall()

  def fetch_one(self):
    '''Fetch one result.'''
    return self.cursor.fetchone()