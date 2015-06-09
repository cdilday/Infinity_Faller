class Simulator(object):

  MOVES = [
      'DOWN',
      'LEFT',
      'RIGHT',
      'NOTHING',
  ]
  
  # ABILITIES = [
  #   'fire_survival',
  # ]

  def __init__(self, design):
    self.elements = design['elements']
    self.specials = design['specials']

  def get_initial_state(self):
    specials_inverted = {what: where for where, what in self.specials.items()}
    initial_position = specials_inverted[0]
    initial_abilities = frozenset()
    return initial_position, initial_abilities

  def get_moves(self):
    return self.MOVES

  def get_next_state(self, state, move):
    pos, abilities = state  

    next_pos = self._resolve_movement(pos, abilities, move)
    # if next_pos in self.specials:
    #   next_abilities = self._upgrade_abilities(abilities, self.specials[next_pos])
    # else:
    #   next_abilities = abilities


    #if self._can_survive_with_abilities(self.elements[next_pos], next_abilities):
    if self.elements[next_pos] is 'A':
      return next_pos, abilities
    else:
      return None

  def _resolve_movement(self, (i,j), abilities, move):
    e = self.elements
    env = (
      e[i-1,j-1],e[i  ,j-1],e[i+1,j-1], # 0, 1, 2
      e[i-1,j  ],e[i  ,j  ],e[i+1,j  ], # 3, 4, 5
      e[i-1,j+1],e[i  ,j+1],e[i+1,j+1], # 6, 7, 8
    )
  
    supported = (env[7] is 'E') or \
      (env[4] is 'W' and 'water_flying' in abilities) or \
      (env[4] is 'A' and 'air_flying' in abilities) \
  
    # ignore movement into a wall
    if move is 'LEFT' and env[3] is 'E':
      move = 'NOTHING'
    elif move is 'RIGHT' and env[5] is 'E':
      move = 'NOTHING'
  
    # check for support from earth or flying
    if not supported:
      if move is 'NOTHING':
        move = 'DOWN'
  
    # ignore upward movement into a way
    if move is 'DOWN' and env[7] is 'E':
      move = 'NOTHING'
  
    # transate moves into new positions
    if   move is 'LEFT':
      if env[6] is 'E' or supported:
        return (i-1,j)
      else:
        return (i-1,j+1)
    elif move is 'RIGHT':
      if env[8] is 'E' or supported:
        return (i+1,j)
      else:
        return (i+1,j+1)
    elif move is 'DOWN':
      return (i,j+1)
    else:
      return (i,j)

  # def _can_survive_with_abilities(self, element, abilities):
  #   if element is 'F':
  #     return 'fire_survival' in abilities
  
  # def _upgrade_abilities(self, abilities, special):
  #   if special is 0 or special is 5:
  #     return abilities # no change for these markers
  #   else:
  #     new_ability = self.ABILITIES[special-1]
  #     if new_ability in abilities:
  #       return abilities
  #     else:
  #       return abilities | frozenset([new_ability])
