'''
Programming Assignment 1 - Database Technology
Olof Enström
oe222fh@student.lnu.se
'''
import csv
import os
import mysql.connector

cnx = mysql.connector.connect(user='root', password='root', host='127.0.0.1')
DB_NAME = 'Enström'
SCRIPT_PATH  = os.path.dirname(os.path.realpath(__file__))
PLANETS_PATH = SCRIPT_PATH + '/data/planets.csv'
SPECIES_PATH = SCRIPT_PATH + '/data/species.csv'

tables = [f'''CREATE TABLE `planets` (
      `name` VARCHAR(45) NOT NULL PRIMARY KEY,
      `rotation_period` INT,
      `orbital_period` INT,
      `diameter` INT,
      `gravity` VARCHAR(50),
      `surface_water` FLOAT,
      `population` BIGINT
    ) ENGINE=InnoDB''',
    f'''CREATE TABLE `climates` (
      `planet` VARCHAR(45) NOT NULL,
      `climate` VARCHAR(45) NOT NULL,
      PRIMARY KEY (`planet`, `climate`),
      FOREIGN KEY (`planet`) REFERENCES `planets` (`name`)
    ) ENGINE=InnoDB''',
    f'''CREATE TABLE `terrains` (
      `planet` VARCHAR(45) NOT NULL,
      `terrain` VARCHAR(45) NOT NULL,
      PRIMARY KEY (`planet`, `terrain`),
      FOREIGN KEY (`planet`) REFERENCES `planets` (`name`)
    ) ENGINE=InnoDB''',
    f'''CREATE TABLE `species` (
      `name` VARCHAR(45) NOT NULL PRIMARY KEY,
      `classification` VARCHAR(45),
      `designation` VARCHAR(45),
      `average_height` INT,
      `average_lifespan` INT,
      `language` VARCHAR(45),
      `homeworld` VARCHAR(45),
      FOREIGN KEY (`homeworld`) REFERENCES `planets` (`name`)
      ) ENGINE=InnoDB''',
    f'''CREATE TABLE `skincolors` (
      `species` VARCHAR(45) NOT NULL,
      `color` VARCHAR(45) NOT NULL,
      PRIMARY KEY (`species`, `color`),
      FOREIGN KEY (`species`) REFERENCES `species` (`name`)
    ) ENGINE=InnoDB''',
    f'''CREATE TABLE `haircolors` (
      `species` VARCHAR(45) NOT NULL,
      `color` VARCHAR(45) NOT NULL,
      PRIMARY KEY (`species`, `color`),
      FOREIGN KEY (`species`) REFERENCES `species` (`name`)
    ) ENGINE=InnoDB''',
    f'''CREATE TABLE `eyecolors` (
      `species` VARCHAR(45) NOT NULL,
      `color` VARCHAR(45) NOT NULL,
      PRIMARY KEY (`species`, `color`),
      FOREIGN KEY (`species`) REFERENCES `species` (`name`)
    ) ENGINE=InnoDB'''
]
cursor = cnx.cursor()

# Global lists for the data.
PLANETS    = []
CLIMATE    = []
TERRAIN    = []
SPECIES    = []
SKINCOLORS = []
HAIRCOLORS = []
EYECOLORS  = []

def createDatabase():
  '''I try to use the database. If it doesn't exist I catch that exception so
  I can create the database, the tables and fill the tables with data.'''
  try:
    cnx.database = DB_NAME
  except Exception:
    print(f'The database "{DB_NAME}" does not exist. Creating it now...')
    cursor.execute(f'CREATE DATABASE {DB_NAME};')
    cnx.database = DB_NAME
    for table in tables:
      cursor.execute(table)
    readFiles()
    fillTables()
    print(f'Database "{DB_NAME}" has been created.')

def readFiles():
  '''
  I open the files and read them with the csv module. If the planet name or species name
  is NA or N/A I consider it as an invalid entry and I do not add it. If other attributes
  have NA or N/A as value I set it to NULL. For climate, terrain, skin_colors, hair_colors
  and eye_colors I extract them so I can create a separate table for each to normalize the
  tables a bit. For the tasks this was unnecessary but for other queries this would make
  it much easier. E.g. "Get all the planets that have the terrain mountains."
  '''
  with open(PLANETS_PATH, 'r', newline='') as csvfile:
    csvfile.readline()
    data = csv.reader(csvfile)
    for row in data:
      row_val = []
      if row[0] in ['NA', 'N/A']:
        continue
      for i, val in enumerate(row):
        if val in ['NA', 'N/A']:
          val = 'NULL'
        if i in [4,6]:
          extraPlanetTables(row[0], val, i)
        else:
          row_val.append(val if val == 'NULL' else '"' + val + '"')
      PLANETS.append(row_val)

  with open(SPECIES_PATH, 'r', newline='') as csvfile:
    csvfile.readline()
    data = csv.reader(csvfile)
    for row in data:
      row_val = []
      if row[0] in ['NA', 'N/A']:
        continue
      for i, val in enumerate(row):
        if val in ['NA', 'N/A', 'indefinite']:
          val = 'NULL'
        if i in [4,5,6]:
          extraSpeciesTables(row[0], val, i)
        else:
          row_val.append(val if val == 'NULL' else '"' + val + '"')
      SPECIES.append(row_val)

def fillTables():
  '''Fill all the tables with the data aquired from the readFiles() function.'''
  keys = "(`name`, `rotation_period`, `orbital_period`, `diameter`, `gravity`, `surface_water`, `population`)"
  for pl in PLANETS:
    cursor.execute(f'''INSERT INTO `planets` {keys} VALUES ({', '.join(pl)});''')
  for cl in CLIMATE:
    cursor.execute(f'''INSERT INTO `climates` (`planet`, `climate`) VALUES ({', '.join(cl)});''')
  for te in TERRAIN:
    cursor.execute(f'''INSERT INTO `terrains` (`planet`, `terrain`) VALUES ({', '.join(te)});''')

  keys = "(`name`, `classification`, `designation`, `average_height`, `average_lifespan`, `language`, `homeworld`)"
  for sp in SPECIES:
    cursor.execute(f'''INSERT INTO `species` {keys} VALUES ({', '.join(sp)});''')
  for sk in SKINCOLORS:
    cursor.execute(f'''INSERT INTO `skincolors` (`species`, `color`) VALUES ({', '.join(sk)});''')
  for ha in HAIRCOLORS:
    cursor.execute(f'''INSERT INTO `haircolors` (`species`, `color`) VALUES ({', '.join(ha)});''')
  for ey in EYECOLORS:
    cursor.execute(f'''INSERT INTO `eyecolors` (`species`, `color`) VALUES ({', '.join(ey)});''')
  cnx.commit()

def mainMenu():
  '''Display a console main menu.'''
  print('''|------------------------------------------------------------------|
| 1. List all planets                                              |
| 2. Search for planet details                                     |
| 3. Search for species with height higher than given number       |
| 4. What is the most likely desired climate of the given species? |
| 5. What is the average lifespan per species classification?      |
| Q. Quit                                                          |
|------------------------------------------------------------------|''')
  inp = input('Please choose an option: ')
  print()
  return inp

def extraPlanetTables(k, v, j):
  '''Here I split the climates and terrains for each planet. So I can add
  that to a separate table. If the value is NULL I don't add it.'''
  v = v.split(', ')
  k = '"' + k + '"'
  for t in v:
    if t == 'NULL':
      continue
    t = '"' + t + '"'
    if j == 4:
      CLIMATE.append([k, t])
    elif j == 6:
      TERRAIN.append([k, t])

def extraSpeciesTables(k, v, j):
  '''Here I split the skincolors, haircolors and eyecolors for each species. So I can add
  that to a separate table. If the value is NULL I don't add it.'''
  v = v.split(', ')
  k = '"' + k + '"'
  for t in v:
    if t == 'NULL':
      continue
    t = '"' + t + '"'
    if j == 4:
      SKINCOLORS.append([k, t])
    elif j == 5:
      HAIRCOLORS.append([k, t])
    elif j == 6:
      EYECOLORS.append([k, t])

def handleInput(inp):
  '''Check the user input and call the appropriate function.'''
  if inp == '1':
    listPlanets()
  elif inp == '2':
    searchPlanet()
  elif inp == '3':
    searchHeight()
  elif inp == '4':
    desiredClimate()
  elif inp == '5':
    speciesLifespan()
  elif inp in ['q', 'Q']:
    print('Bye bye!')
    return
  input('\nPress any key and ENTER to return to the menu...')
  handleInput(mainMenu())

def listPlanets():
  '''I select the name from planets and order it by name. Then I just
  loop through the rows and print the name of every planet.'''
  cursor.execute('SELECT name FROM planets ORDER BY name;')
  rows = cursor.fetchall()
  print('List of planets\n---------------')
  for tup in rows:
    print(tup[0])

def searchPlanet():
  '''Here is a task that got more complicated by splitting the climates and terrains
  in to separate tables. Planets that got multiple climates and terrain I want to
  show that information on the same row. I don't want a row with all planet details
  for every climate and terrain. So I GROUP_CONCAT the climate from the climates
  table and the terrain from the terrains table and GROUP BY the planet. I make a
  left outer join for both tables as I still want to show planet details even if
  the planet doesn't have any climates or terrains. I also decided to use LIKE so
  you don't have to type the whole name of the planet you are searching for and
  you can get details about multiple planets at the same time. I could just do
  three separate queries that gets the details, climates and terrains. Then just
  format it with Python instead of doing it in a single execute.
  '''
  search = input('Enter planet name: ')
  q = '%' + search + '%'
  cursor.execute('''
                SELECT planets.*, climate, terrain
                FROM planets
                LEFT OUTER JOIN
                (SELECT planet, GROUP_CONCAT(climate) AS climate FROM climates GROUP BY planet) AS t1 ON planets.name = t1.planet
                LEFT OUTER JOIN
                (SELECT planet, GROUP_CONCAT(terrain) AS terrain FROM terrains GROUP BY planet) AS t2 ON planets.name = t2.planet
                WHERE name LIKE %s;
                ''',(q,))
  rows = cursor.fetchall()
  columns = cursor.description
  print(f'Showing results for: "{search}"')
  print('-----------------------' + '-' * len(search))
  for tup in rows:
    for i, v in enumerate(tup):
      print(columns[i][0] + ':' + (' ' * (15 - len(columns[i][0]))) + ' ' + str(v))
    print('-----------------------' + '-' * len(search))

def searchHeight():
  '''I select the name and average_height from species where
  the average_height is larger than the given input. I also
  order it to get the largest average_height at the top.'''
  search = input('Enter an average height: ')
  if not search.isdigit():
    return
  cursor.execute('''
                SELECT name, average_height
                FROM species
                WHERE average_height > %s
                ORDER BY average_height DESC;''',
                (search,))
  rows = cursor.fetchall()
  print('Species with an average height above', search)
  print('-' * len(search) + '-------------------------------------')
  for tup in rows:
    print(tup[0], (' ' * (15 - len(tup[0]))), f'({tup[1]})')

def desiredClimate():
  '''I select the climate from the climates table and join it with species where
  the species homeworld matches the climates planet. This gives me the most
  likely desired climate(s) of the species.'''
  search = input('Enter a species: ')
  cursor.execute('''
                SELECT climate
                FROM climates
                JOIN species ON species.homeworld = climates.planet
                WHERE species.name = %s;
                ''', (search,))
  rows = cursor.fetchall()
  print(f'The most likely desired climate(s) of "{search}" is/are:')
  if len(rows) == 0:
    print('No results found!')
  else:
    print(', '.join(map(lambda x: x[0], rows)))

def speciesLifespan():
  '''I select the classification and the aggregate function AVG on the average_lifespan.
  I don't select the rows where classification and average_lifespan are NULL as I
  don't want to show rows that doesn't have an average_lifespan. I then GROUP BY
  classification so the average gets calculated correctly. I also order it by the
  average to get the classification with the highest average at the top.'''
  cursor.execute('''
                SELECT classification, AVG(average_lifespan) AS avg
                FROM species
                WHERE classification IS NOT NULL
                AND average_lifespan IS NOT NULL
                GROUP BY classification
                ORDER BY avg DESC;
                ''')
  rows = cursor.fetchall()
  print('Species \tAverage lifespan\n--------------------------------')
  for tu in rows:
    print(tu[0] + '  \t' + str(round(tu[1], 2)))

def main():
  '''Main function'''
  createDatabase()
  handleInput(mainMenu())
  cnx.close()

if __name__ == '__main__':
  main()