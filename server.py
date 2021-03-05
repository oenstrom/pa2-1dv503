from flask import Flask, render_template, abort, request
import mysql.connector
import json
from dbconnection import DBConnection

cnx = DBConnection('root', 'root', '127.0.0.1')
cnx.create_database('Enström')
##############################################################


# Create all tables and vies and fill them with data.
cnx.create_tables('data/tables.sql')
cnx.fill_table('data/csv/pokemon.csv', 'pokemon')
cnx.fill_table('data/csv/type.csv', 'type')
cnx.fill_table('data/csv/move.csv', 'move')
cnx.fill_table('data/csv/effectiveness.csv', 'effectiveness')
cnx.fill_table('data/csv/move_type.csv', 'move_type')
cnx.fill_table('data/csv/pokemon_move.csv', 'pokemon_move')
cnx.fill_table('data/csv/pokemon_type.csv', 'pokemon_type')

app = Flask(__name__)

def rgb_from_hex(c_hex):
  '''Convert hex color to rgb.'''
  return tuple(int(c_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def get_fg_color(rgb):
  '''Calculate foreground color based on rgb color.'''
  if rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114 > 186:
    return '#000000'
  else:
    return '#ffffff'

def get_color(hex_color):
  '''Get rgb bg color and foreground color.'''
  rgb_color = rgb_from_hex(hex_color)
  fg_color = get_fg_color(rgb_color)
  return {'bg': rgb_color, 'fg': fg_color}

def fix_pokemon_type(pokemon_list):
  '''Convert pokemon type/color json into dict.'''
  for p in pokemon_list:
    p['type_color'] = json.loads(p['type_color'])
    for k, v in p['type_color'].items():
      p['type_color'][k] = get_color(v)
  return pokemon_list

def pokemon_query(cond='', params=tuple()):
  '''Query for getting information about one or all pokemons.'''
  cnx.run(f'''
          SELECT
            id, name, hit_points, attack, defense, special_attack, special_defense, speed,
            (hit_points + attack + defense + special_attack + special_defense + speed) AS sum,
            JSON_OBJECTAGG(type, color) AS type_color
          FROM pokemon_with_type
          {cond}
          GROUP BY id;''', params)
  return cnx.fetch_all()

@app.route('/', methods=['GET'])
def index():
  '''Route for searching for pokemons and moves.'''
  search_word = request.args.get('q')
  if not search_word:
    return render_template('index.html', search=search_word)
  else:
    search_word = f'%{search_word}%'
    cnx.run('SELECT id, name FROM pokemon WHERE id LIKE %s OR name LIKE %s ORDER BY id;', (search_word, search_word))
    pokemons = cnx.fetch_all()
    cnx.run('SELECT id, name FROM move WHERE name LIKE %s ORDER BY name;', (search_word,))
    moves = cnx.fetch_all()
    return render_template('index.html', pokemons=pokemons, moves=moves, search=search_word.strip('%'))

@app.route('/pokemon/')
def show_all_pokemons():
  '''Route for displaying information about all pokemons.'''
  pokemons = fix_pokemon_type(pokemon_query())
  return render_template('pokemon.html', pokemons=pokemons)

@app.route('/pokemon/<var>/')
def show_one_pokemon(var):
  '''Route for displaying one pokemon, damage taken and which moves it can learn.'''
  pokemon = fix_pokemon_type(pokemon_query('WHERE name = %s OR id = %s', (var, var)))[0]
  if not pokemon:
    abort(404)

  cnx.run('SELECT * FROM move_with_type JOIN pokemon_move ON id = move_id WHERE pokemon_id = %s ORDER BY level, learned_by DESC;', (pokemon['id'],))
  moves = cnx.fetch_all()
  for mv in moves:
    mv['color'] = get_color(mv['color'])

  effectiveness = []
  where = '' if len(pokemon['type_color']) == 1 else 'OR defending_name = %s'
  params = tuple(pokemon['type_color'].keys())
  cnx.run(f'SELECT attacking_id, attacking_name, MAX(attacking_color) AS attacking_color, JSON_ARRAYAGG(modifier) AS modifier FROM effectiveness_with_type WHERE defending_name = %s {where} GROUP BY attacking_id;', params)
  effectiveness += cnx.fetch_all()
  for row in effectiveness:
    row['attacking_color'] = get_color(row['attacking_color'])
    mod = json.loads(row['modifier'])
    row['modifier'] = mod[0] if len(mod) == 1 else mod[0] * mod[1]

  return render_template('one-pokemon.html', pokemon=pokemon, moves=moves, effectiveness=effectiveness)

@app.route('/move/')
def show_all_moves():
  '''Route for displaying information about all moves.'''
  cnx.run('SELECT * FROM move_with_type ORDER BY name;')
  moves = cnx.fetch_all()
  for mv in moves:
    mv['color'] = get_color(mv['color'])
  return render_template('move.html', moves=moves)

@app.route('/move/<var>/')
def show_one_move(var):
  '''Route for displaying one move, move effectiveness and which pokemon that can learn it.'''
  cnx.run('SELECT * FROM move_with_type WHERE name = %s OR id = %s;', (var, var))
  move = cnx.fetch_one()
  if not move:
    abort(404)
  
  cnx.run(f'SELECT defending_id, defending_name, MAX(defending_color) AS defending_color, MAX(modifier) AS modifier FROM effectiveness_with_type WHERE attacking_name = %s GROUP BY defending_id;', (move['type'],))
  effectiveness = cnx.fetch_all()
  for row in effectiveness:
    row['defending_color'] = get_color(row['defending_color'])
  
  move['color'] = get_color(move['color'])
  cnx.run('SELECT * FROM pokemon_move JOIN pokemon ON pokemon_id = id WHERE move_id = %s;', (move['id'],))
  pokemons = cnx.fetch_all()
  return render_template('one-move.html', move=move, pokemons=pokemons, effectiveness=effectiveness)