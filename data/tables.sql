DROP TABLE IF EXISTS `pokemon_type`;
DROP TABLE IF EXISTS `pokemon_move`;
DROP TABLE IF EXISTS `move_type`;
DROP TABLE IF EXISTS `effectiveness`;
DROP TABLE IF EXISTS `move`;
DROP TABLE IF EXISTS `type`;
DROP TABLE IF EXISTS `pokemon`;


CREATE TABLE `pokemon` (
  `id` int unsigned NOT NULL,
  `name` varchar(50) NOT NULL,
  `hit_points` int unsigned NOT NULL,
  `attack` int unsigned NOT NULL,
  `defense` int unsigned NOT NULL,
  `special_attack` int unsigned NOT NULL,
  `special_defense` int unsigned NOT NULL,
  `speed` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `type` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `color` varchar(7) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `move` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `power` int unsigned,
  `accuracy` int unsigned,
  `power_points` int unsigned,
  `description` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `effectiveness` (
  `attacking_type_id` int unsigned NOT NULL,
  `defending_type_id` int unsigned NOT NULL,
  `modifier` decimal(5,2) unsigned NOT NULL,
  FOREIGN KEY (`attacking_type_id`) REFERENCES `type` (`id`),
  FOREIGN KEY (`defending_type_id`) REFERENCES `type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `move_type` (
  `move_id` int unsigned NOT NULL,
  `type_id` int unsigned NOT NULL,
  FOREIGN KEY (`move_id`) REFERENCES `move` (`id`),
  FOREIGN KEY (`type_id`) REFERENCES `type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `pokemon_move` (
  `pokemon_id` int unsigned NOT NULL,
  `move_id` int unsigned NOT NULL,
  `level` int unsigned DEFAULT NULL,
  `learned_by` varchar(20) NOT NULL,
  FOREIGN KEY (`pokemon_id`) REFERENCES `pokemon` (`id`),
  FOREIGN KEY (`move_id`) REFERENCES `move` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


CREATE TABLE `pokemon_type` (
  `pokemon_id` int unsigned NOT NULL,
  `type_id` int unsigned NOT NULL,
  FOREIGN KEY (`pokemon_id`) REFERENCES `pokemon` (`id`),
  FOREIGN KEY (`type_id`) REFERENCES `type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE OR REPLACE VIEW pokemon_with_type AS
  SELECT
    pokemon.*,
    type.name AS type,
    type.color
  FROM pokemon
  JOIN pokemon_type
    ON pokemon_id = pokemon.id
  JOIN type
    ON type_id = type.id;

CREATE OR REPLACE VIEW effectiveness_with_type AS
  SELECT
    effectiveness.attacking_type_id AS attacking_id,
    t1.name AS attacking_name,
    t1.color AS attacking_color,
    effectiveness.modifier,
    effectiveness.defending_type_id AS defending_id,
    t2.name AS defending_name,
    t2.color AS defending_color
  FROM effectiveness
  JOIN type t1 ON t1.id = attacking_type_id
  JOIN type t2 ON t2.id = defending_type_id;

CREATE OR REPLACE VIEW move_with_type AS
  SELECT
    move.id,
    move.name,
    power,
    accuracy,
    power_points,
    description,
    type.name AS type,
    type.color
  FROM move
  JOIN move_type ON move.id = move_id
  JOIN type ON type.id = type_id;