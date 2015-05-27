from p6_game import Simulator
from heapq import heappush, heappop
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

import p6_tool

ANALYSIS = {}

def analyze(design):
	sim = Simulator(design)
	init = sim.get_initial_state()

	#BFS
	ANALYSIS = {init: None}

	q = Q.PriorityQueue()

	q.put((0, init[0], init[1]))

	while not q.empty():
		node = q.get()
		#no goal state required as we're doing an exhaustive search

		moves = sim.get_moves()
		#see all possible states for each move
		states = []
		for move in moves:
			#NONETYPE not iterable error
			#print node
			if sim.get_next_state((node[1],node[2]), move) != None:
				pos, abil = sim.get_next_state((node[1],node[2]), move)
				value = 1
				#check if it's moved diagonally downward and add distance accordingly
				if pos[1] > node[1][1] and pos[0] != node[1][0]:
					value = 1.2
				newState = (node[0] + value, pos, abil)
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
	paths = []
	for node in report:
		if node[0] == (i, j):
			currNode = node
			offset = p6_tool.make_offset()
			color = p6_tool.make_color()
			while report[currNode] != None:
				draw_line(currNode[0], report[currNode][0], offset, color)
				currNode = report[currNode]
			
	# TODO: use ANALYSIS and (i,j) draw some lines

	#raise NotImplementedError
