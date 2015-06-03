from traceback import print_exc
from Tkinter import *
from random import random, randint
from collections import defaultdict

import p6_analysis
import copy

TILE_SIZE = 16
canvas = None
design = None
turn = 0
turns_to_move = 2
playerLoc = None
path = None

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

def make_color():
  return '#'+hex(randint(256,4096))[2:]

OFFSETS = defaultdict(make_offset)
COLORS = defaultdict(make_color)

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
    color = COLORS[color_obj]
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
    global turn
    global design
    #print design
    if path == None:
      print "no path"
    if design == None:
      print "no path"
    if turn == None:
      print "no path"
    result = take_turn(design, turn, path[-1])
    turn = result[0]
    design = result[1]
    del path[-1]
    display_design_on_canvas(canvas, design)




    # display_design_on_canvas(canvas, design)

  def enter(event):
    canvas.delete('inspection')
    item = event.widget.find_closest(event.x, event.y)[0]
    #coords = rect_coords[item]
    #i,j = coords

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
          #print graph[x,y]
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
      path = p6_analysis.inspect(report, coords, draw_inspection_line)
    except:
      print_exc()

  canvas.bind('<ButtonPress-1>',click)
  canvas.tag_bind('tile','<Enter>',enter)
  
  try:
    report = p6_analysis.analyze(design)
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
  playerPlace = level['specials'].items()[0][0]
  #print "moved player from old position: ", playerLoc
  playerPlace = ((i, j))
  #print "to new position: ", playerLoc
  level['specials'] = {}
  level['specials'][playerPlace] = 0
  return level


def take_turn(board, turnNum, (i, j)):
  newBoard = copy.copy(board)
  turnNum += 1
  if i is None:
    print "Waiting"
  else:
    newBoard = move_player((i,j), newBoard)
    #del path[-1]
  if turnNum % turns_to_move == 0:
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

    newBoard['elements'] = graph
  return (turnNum, newBoard)

def print_map(board):
  for y in range(0, board['height']):
    tempstr = ""
    for x in range(0, board['width']):
      tempstr = tempstr + board['elements'][x,y]
    print tempstr
def main(argv):

  prog, filename = argv 
  global design 
  design = load_design(filename)

  master = Tk()
  master.title("Tears of the Mantis: Fall to Chaos")

  w, h = TILE_SIZE*design['width'], TILE_SIZE*design['height']
  global canvas
  canvas = Canvas(master, width=w, height=h)
  canvas.pack()

  display_design_on_canvas(canvas, design)

  master.bind('<Escape>', lambda event: master.quit())

  master.mainloop()


if __name__ == '__main__':
  import sys
  main(sys.argv)
