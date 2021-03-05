import csv
import json

types = {
  'Normal': 1,
  'Fighting': 2,
  'Flying': 3,
  'Poison': 4,
  'Ground': 5,
  'Rock': 6,
  'Bug': 7,
  'Ghost': 8,
  'Steel': 9,
  'Fire': 10,
  'Water': 11,
  'Grass': 12,
  'Electric': 13,
  'Psychic': 14,
  'Ice': 15,
  'Dragon': 16,
  'Dark': 17,
  'Fairy': 18
}


pokemons = []
pokemon_types = []
pokemon_moves = []
moves = []
move_types = []
with open('data/pokedex.json') as f:
  test = json.load(f)
  for row in test:
    if int(row['Id']) > 151:
      break
    row['Id'] = int(row['Id'])
    pokemons.append({
      'id': row['Id'],
      'name': row['Name'],
      'hit_points': row['HP'],
      'attack': row['Attack'],
      'defense': row['Defense'],
      'special_attack': row['Sp. Attack'],
      'special_defense': row['Sp. Defense'],
      'speed': row['Speed']
    })
    pokemon_types.append({'pokemon_id': row['Id'], 'type_id': types[row['Type 1']]})
    if row['Type 2'] != 'None':
      pokemon_types.append({'pokemon_id': row['Id'], 'type_id': types[row['Type 2']]})

    for mv in row['Moves']:
      level = row['Moves'][mv]['Level']
      pokemon_moves.append({
        'pokemon_id': row['Id'],
        'move_id': mv,
        'level': level if level.isdigit() else None,
        'learned_by': 'Level' if level.isdigit() else ('Starts with' if level == '—' else level)
      })
      power = row['Moves'][mv]['Power']
      accuracy = row['Moves'][mv]['Accuracy']
      pp = row['Moves'][mv]['PP']
      moves.append({
        'name': mv,
        'type': row['Moves'][mv]['Type'],
        'power': power if power.isdigit() else None,
        'accuracy': accuracy if accuracy.isdigit() else None,
        'power_points': pp if pp.isdigit() else None,
        'description': row['Moves'][mv]['Description']
        })

moves = list({v['name']:v for v in moves}.values())
moves = sorted(moves, key=lambda k: k['name'])
for i, k in enumerate(moves):
  k['id'] = i+1
  move_types.append({'move_id': i+1, 'type_id': types[k['type']]})
  k.pop('type', None)

for pm in pokemon_moves:
  for m in moves:
    if pm['move_id'] == m['name']:
      pm['move_id'] = m['id']



#################
# Write to files
#################
with open('data/csv/pokemon.csv', 'w', newline='') as f:
  fieldnames = ['id', 'name', 'hit_points', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()
  for row in pokemons:
    writer.writerow(row)

with open('data/csv/pokemon_type.csv', 'w', newline='') as f:
  fieldnames = ['pokemon_id', 'type_id']
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()
  for row in pokemon_types:
    writer.writerow(row)

with open('data/csv/pokemon_move.csv', 'w', newline='') as f:
  fieldnames = ['pokemon_id', 'move_id', 'level', 'learned_by']
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()
  for row in pokemon_moves:
    writer.writerow(row)

with open('data/csv/move.csv', 'w', newline='') as f:
  fieldnames = ['id', 'name', 'power', 'accuracy', 'power_points', 'description']
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()
  for row in moves:
    writer.writerow(row)

with open('data/csv/move_type.csv', 'w', newline='') as f:
  fieldnames = ['move_id', 'type_id']
  writer = csv.DictWriter(f, fieldnames=fieldnames)
  writer.writeheader()
  for row in move_types:
    writer.writerow(row)
