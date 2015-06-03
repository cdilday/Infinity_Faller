from p6_game import Simulator
from heapq import heappush, heappop
import copy
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

import p6_tool

ANALYSIS = {}

turns_to_move = p6_tool.turns_to_move
def analyze(thing):
	tempDesign = copy.deepcopy(thing)
	sim = Simulator(tempDesign)
	init = sim.get_initial_state()


	ANALYSIS = {init: None}

	q = Q.PriorityQueue()
	q.put((0, init[0], init[1], 0, tempDesign, sim))

	while not q.empty():
		node = q.get()
		#no goal state required as we're doing an exhaustive search
		#(distance from start, (point), abilities)
		#(distance from start, (point), abilities, turn number, newDesign, sim) 

		moves = node[5].get_moves()
		#see all possible states for each move
		states = []
		for move in moves:
			if node[5].get_next_state((node[1],node[2]), move) != None:
				pos, abil = node[5].get_next_state((node[1],node[2]), move)
				value = 1
				#check if it's moved diagonally downward and add distance accordingly
				if pos[1] > node[1][1] and pos[0] != node[1][0]:
					value = 1.2
				tempResult = p6_tool.take_turn(copy.copy(node[4]), node[3], pos)
				tempTurn = tempResult[0]
				tempMap = tempResult[1]
				pos = (tempMap['specials'].items()[0][0])
				tempSim = Simulator(tempMap)
				newState = (node[0] + value, pos, abil, tempTurn, tempMap, tempSim)
				states.append(newState)

		#Use ANALYSIS like a prev dict, only each key now has states so the solution will be unique for each set of abilities
		for state in states:
			curr = (state[1],state[2])
			if curr not in ANALYSIS:
				ANALYSIS[curr] = (node[1],node[2])
				q.put(state)
	return ANALYSIS
	# TODO: fill in this function, populating the ANALYSIS dict
	#raise NotImplementedError

def inspect(report, (i,j), draw_line):
	#search the dict for every solution that starts with that pos, the build paths from each soltion back to the start
	#print (i,j)
	path = []
	for node in report:
		if node[0] == (i, j):
			currNode = node
			offset = (0,0)
			color = p6_tool.make_color()
			while report[currNode] != None:
				path.append(currNode[0])
				draw_line(currNode[0], report[currNode][0], offset, color)
				currNode = report[currNode]
	
	return path
	#raise NotImplementedError