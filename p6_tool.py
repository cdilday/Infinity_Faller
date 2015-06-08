from traceback import print_exc
from Tkinter import *
from random import random, randint
from collections import defaultdict

import p6_analysis
import copy
import time

new_turn = False
cant_path = False
TILE_SIZE = 16
canvas = None
design = None
turn = 0
turns_to_move = 2
playerLoc = None
path = None
new_elements = {}
line_counter = 0
MAP_HEIGHT = 0
MAP_WIDTH = 0

ELEMENT_COLORS = {
  'E': 'black',
  'W': 'blue',
  'A': 'white',
  'F': 'orange',
}

ELEMENT_LIST = list('EWAF')

def make_offset():
  return TILE_SIZE*(0.125+0.75*random()), \
         TILE_SIZE*(0.125+0.75*random())

def make_color1():
  return '#00FFFF'

def make_color2():
  return '#FF0000'

OFFSETS = defaultdict(make_offset)
#COLORS = defaultdict(make_color)

def next_element(e):
  return ELEMENT_LIST[(ELEMENT_LIST.index(e)+1) % len(ELEMENT_LIST)]

def display_design_on_canvas(canvas, design):
  canvas.delete(ALL)

  width, height = design['width'], design['height']
  elements = design['elements']
  specials = design['specials']

  rect_coords = {}
  for i in range(width):
    for j in range(height):
      bbox = (TILE_SIZE*i, TILE_SIZE*j, TILE_SIZE*(i+1), TILE_SIZE*(j+1))
      color = ELEMENT_COLORS[elements[i,j]]
      rect = canvas.create_rectangle(bbox, fill=color, tags=('tile',), outline='')
      rect_coords[rect] = (i,j)

  shrink = 1
  for (i,j),k in specials.items():
    bbox = (TILE_SIZE*i+shrink, TILE_SIZE*j+shrink, TILE_SIZE*(i+1)-shrink, TILE_SIZE*(j+1)-shrink)
    canvas.create_oval(bbox, fill='', outline='red',width=2)

  def draw_inspection_line((i1,j1),(i2,j2),offset_obj=None, color_obj=None):
    oi, oj = OFFSETS[offset_obj]
    color = color_obj
    canvas.create_line(
        TILE_SIZE * i1 + oi,
        TILE_SIZE * j1 + oj,
        TILE_SIZE * i2 + oi,
        TILE_SIZE * j2 + oj,
        tags=('inspection',),
        fill=color,
        width=4,
    )

  def click(event):
    # item = event.widget.find_closest(event.x, event.y)[0]
    # coords = rect_coords[item]
    # elements[coords] = next_element(elements[coords])
    global cant_path
    global new_turn
    if cant_path and new_turn:
      cant_path = False
    global turn
    global design
    deletion = False

    #print design
    result = None
    if len(path) is 0 or cant_path:
      if not cant_path:
        print "drawing new path"
        redraw_path()
      if len(path) is 0:
        result = take_turn(design, turn, design['specials'].items()[0][0])
        cant_path = True
      else:
        result = take_turn(design, turn, path[-1])
        deletion = True
    else:
      result = take_turn(design, turn, path[-1])
      deletion = True
    
    new_turn = result[2]
    global new_elements
  
    if len(path) is 0 and len(new_elements) is 0:
      new_elements = generate_map(MAP_WIDTH, MAP_HEIGHT)


    turn = result[0]
    design = result[1]
    global playerLoc
    playerLoc = design['specials'].items()[0][0]
    #display_design_lite(canvas, design)
    elements = design['elements']
    specials = design['specials']

    rect_coords = {}
    for i in range(width):
      for j in range(height):
        bbox = (TILE_SIZE*i, TILE_SIZE*j, TILE_SIZE*(i+1), TILE_SIZE*(j+1))
        color = ELEMENT_COLORS[elements[i,j]]
        rect = canvas.create_rectangle(bbox, fill=color, tags=('tile',), outline='')
        rect_coords[rect] = (i,j)

    shrink = 1
    for (i,j),k in specials.items():
      bbox = (TILE_SIZE*i+shrink, TILE_SIZE*j+shrink, TILE_SIZE*(i+1)-shrink, TILE_SIZE*(j+1)-shrink)
      canvas.create_oval(bbox, fill='', outline='red',width=2)

    p6_analysis.draw_path(path, draw_inspection_line, turn)
    if deletion:
      del path[-1]

  def enter(event):
    filler = 1+1
    #item = event.widget.find_closest(event.x, event.y)[0]
    #coords = rect_coords[item]

    # try:
    #   global path
    #   path = p6_analysis.analyze_specific(design, coords)
    #   p6_analysis.draw_path(path, draw_inspection_line)
    # except:
    #   print_exc()

  canvas.bind('<ButtonPress-1>',click)
  canvas.tag_bind('tile','<Enter>',enter)
  
  coords = (0,0)

  #override coords with lowest platform goal
  found = False
  y = height - 2
  graph = design['elements']
  #print_map(design)
  while y > 1:
    x = 1
    while x < width - 1:
      if graph[x,y] == 'E':
        #check to make sure it's empty above it
        if graph[x, y-1] != 'E':
          coords = x, y-1
          found = True
          break
      x += 1
    if found:
      break
    y -= 1
    #print coords

  i,j = coords
  bbox = (TILE_SIZE*i, TILE_SIZE*j, TILE_SIZE*(i+1), TILE_SIZE*(j+1))
  canvas.create_rectangle(bbox, outline='gray', tags=('inspection',), width=2)

  try:
    global path
    path = p6_analysis.analyze_specific(design, coords)
    p6_analysis.draw_path(path, draw_inspection_line, turn)
  except:
    print_exc()

  def redraw_path():
    coords = (0,0)
    global design
    #override coords with lowest platform goal
    found = False
    y = design['height'] - 2
    graph = design['elements']
    #print_map(design)
    while y > 1:
      x = 1
      while x < design['width'] - 1:
        if graph[x,y] == 'E':
          #check to make sure it's empty above it
          if graph[x, y-1] != 'E':
            coords = x, y-1
            found = True
            break
        x += 1
      if found:
        break
      y -= 1
      #print coords

    i,j = coords
    bbox = (TILE_SIZE*i, TILE_SIZE*j, TILE_SIZE*(i+1), TILE_SIZE*(j+1))
    global canvas
    canvas.create_rectangle(bbox, outline='gray', tags=('inspection',), width=2)

    try:
      global path
      path = p6_analysis.analyze_specific(design, coords)
      p6_analysis.draw_path(path, draw_inspection_line, turn)
    except:
      print_exc()


def load_design(filename):
  with open(filename) as f:
    lines = f.readlines()

  char_table = [list(line.strip().replace(' ', '')) for line in lines]
  rows = len(char_table)
  cols = len(char_table[0])
  specials = {}
  elements = {}
  for j in range(rows):
    for i in range(cols):
      char = char_table[j][i]
      if char not in 'EAWF':
        specials[i,j] = int(char)
        char_table[j][i] = 'A'
      elements[i,j] = char_table[j][i]

  return {'elements': elements, 'specials': specials, 'width': cols, 'height': rows}

def move_player((i,j), level):
  #newGraph = level['elements']
  #playerPlace = level['specials'].items()[0][0]
  #print "moved player from old position: ", playerLoc
  playerPlace = ((i, j))
  #print "to new position: ", playerLoc
  level['specials'] = {}
  level['specials'][playerPlace] = 0
  return level


def take_turn(board, turnNum, pos):
  movedBoard = False
  newBoard = copy.copy(board)
  turnNum += 1
  waiting = False

  playerLoc = (newBoard['specials'].items()[0][0])
  if pos is playerLoc:
    print "Waiting"
    waiting = True

  else:
    newBoard = move_player(pos, newBoard)
    #del path[-1]
  if turnNum % turns_to_move == 0:
    movedBoard = True
    #move board up
    #first check if player needs to be moved up because they're on the ground
    playerLoc = (newBoard['specials'].items()[0][0])
    graph = newBoard['elements']
    if graph[(playerLoc[0], playerLoc[1] + 1)] is 'E':
      playerLoc = (playerLoc[0], playerLoc[1] - 1)
    newBoard['specials'] = {}
    newBoard['specials'][playerLoc] = 0
    #now move the main portion of the map upwards
    y = 2
    while y < newBoard['height'] - 3:
      x = 0
      while x < newBoard['width']:
        graph[x, y] = graph[x, y+1]
        x += 1
      y += 1

    
    fill_bottom_row(board, waiting)

    newBoard['elements'] = graph
  return (turnNum, newBoard, movedBoard)

def fill_bottom_row(board, no_path):
   # use this to load in levels from the generated design
  # right now we'll just load it with empties until we get that implemented

  global new_elements
  global line_counter

  if 2 + line_counter == board['height']-2 :
    line_counter = 0

  player_x, player_y = board['specials'].items()[0][0]
  

  for x in range(0, board['width']):
    #board['elements'][x, board['height'] - 3] = 'A'
    if (x == 0 or x == board['width'] - 1 ):
      board['elements'][x, board['height'] - 3] = 'E'
    elif len(new_elements) is 0:
      board['elements'][x, board['height'] - 3] = 'A'
    else:
      board['elements'][x, board['height'] - 3] = new_elements[x, 2+line_counter]
      del new_elements[x, 2+line_counter]

  # if the player is at upper half of the canvas and no path, draw a reachable platform 
  if (player_y <= int((board['height'] -3)/2)  and no_path):
    reachable_x = randint(max(1,player_x-2), min(player_x+2, board['width'] - 1))
    print "reachable ensured"
    board['elements'][reachable_x, board['height'] - 3] = 'E'
    board['elements'][reachable_x+1, board['height'] - 3] = 'E'

  line_counter += 1


def print_map(board):
  for y in range(0, board['height']):
    tempstr = ""
    for x in range(0, board['width']):
      tempstr = tempstr + board['elements'][x,y]
    print tempstr

def generate_map(width, height):
  ''' 
    generate platforms in every two columns for a new level/elements dictionary

    prev: MAP_WIDTH and MAP_HEIGHT
    post: a dictionary with generated E elements 
  '''

  elements = {}

  for y_room in range(2, height-2):

    for x_room in range(1, width-1):
      elements[x_room, y_room] = 'A'

    if y_room % 2 == 0:
      rand_x = randint(1, width-1-1) 

      elements[rand_x, y_room] = 'E'
      if rand_x+1 != width-1: 
        elements[rand_x+1, y_room] = 'E'

  return elements

  
  # # two horizontal edges
  # for row in range(width): # range (x,y) --> x <= n < y
  #   #print elements[row,0]
  #   elements[row, 0] = 'E'
  #   elements[row, height-1] = 'E' # height - 1 is the lowest index
  #   # first_row_box = (TILE_SIZE*row, TILE_SIZE*0, TILE_SIZE*(row+1), TILE_SIZE*(1))
  #   # last_row_box = (TILE_SIZE*row, TILE_SIZE*height-1, TILE_SIZE*(row+1), TILE_SIZE*(height-1+1))
    
  #   # f_color = ELEMENT_COLORS['E']
  #   # l_color = ELEMENT_COLORS['E']
  #   # f_rect = canvas.create_rectangle(first_row_box, fill=f_color, tags=('tile',), outline='')
  #   # l_rect = canvas.create_rectangle(last_row_box, fill=l_color, tags=('tile',), outline='')
  #   # rect_coords[f_rect] = (row,0)
  #   # rect_coords[l_rect] = (row,height-1)

  # # two vertical edges
  # for col in range(height): 
  #   elements[0, col] = 'E'
  #   elements[width-1, col] = 'E' # width - 1 is the right most index
  #   # first_col_box = (TILE_SIZE*0, TILE_SIZE*col, TILE_SIZE*(0+1), TILE_SIZE*(col+1))
  #   # last_col_box = (TILE_SIZE*width-1, TILE_SIZE*col, TILE_SIZE*(width-1+1), TILE_SIZE*(col+1))
  #   # f_olor = ELEMENT_COLORS['E']
  #   # l_olor = ELEMENT_COLORS['E']
  #   # f_rect = canvas.create_rectangle(first_col_box, fill=f_color, tags=('tile',), outline='')
  #   # l_rect = canvas.create_rectangle(last_col_box, fill=l_color, tags=('tile',), outline='')
  #   # rect_coords[first_col_box] = (0,col)
  #   # rect_coords[last_col_box] = (width-1,col)

  # # assign dead zone 
  # for dead_zone in range (1, width-1): 
  #   elements[dead_zone, 1] = 'F'
  #   elements[dead_zone, height-2] = 'F'
  #   # top_dead_box = (TILE_SIZE*dead_zone, TILE_SIZE*1, TILE_SIZE*(dead_zone+1), TILE_SIZE*(1+1))
  #   # bot_dead_box = (TILE_SIZE*dead_zone, TILE_SIZE*(height-2), TILE_SIZE*(dead_zone+1), TILE_SIZE*(height-2+1))
  #   # t_color = ELEMENT_COLORS['F']
  #   # b_color = ELEMENT_COLORS['F']
  #   # t_rect = canvas.create_rectangle(top_dead_box, fill=t_color, tags=('tile',), outline='')
  #   # b_rect = canvas.create_rectangle(bot_dead_box, fill=b_color, tags=('tile',), outline='')
  #   # rect_coords[t_rect] = (dead_zone,1)
  #   # rect_coords[b_rect] = (dead_zone,height-2)


      # if randint(0, 10) > 5:
      #   elements[rand_x+2, y_room] = 'E'


  # for e in range(max_earth+1):
  #   rand_x = randint(1, width-1)
  #   rand_y = randint(2, height-2-1)
  #   #if specials[(rand_x, rand_y)] is None:
  #   elements[rand_x, rand_y] = 'E'
  #   elements[rand_x+1, rand_y] = 'E'
  

  # specials[(3,3)] = 0
  # elements[(3,3)] = 'A'
  # elements[(3,4)] = 'E'

  #return {'elements': elements, 'specials': specials, 'width': width, 'height': height}


def main(argv):

  prog, filename = argv 
  global design 
  design = load_design(filename)

  master = Tk()
  master.title("Infinity Fall")

  w, h = TILE_SIZE*design['width'], TILE_SIZE*design['height']

  global MAP_WIDTH
  global MAP_HEIGHT

  MAP_WIDTH = design['width']  # current is 18 by 22
  MAP_HEIGHT = design['height']

  # design = {}
  
  # design = generate_map(width, height)
  global canvas
  canvas = Canvas(master, width=w, height=h)
  canvas.pack()

  global new_elements
  new_elements = generate_map(MAP_WIDTH, MAP_HEIGHT)
  

  display_design_on_canvas(canvas, design)

  master.bind('<Escape>', lambda event: master.quit())

  master.mainloop()


if __name__ == '__main__':
  import sys
  main(sys.argv)
