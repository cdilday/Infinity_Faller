from p6_game import Simulator
from heapq import heappush, heappop
import copy
import math
import time
try:
    import Queue as Q  # ver. < 3.0
except ImportError:
    import queue as Q

from heapq import heappush, heappop
import p6_tool

ANALYSIS = {}

turns_to_move = p6_tool.turns_to_move

def turns_number(turns):
	global turns_to_move
	return	int(turns / turns_to_move)

def is_falling(player_y, next_y):
	''' 
		if the next state is moving down, return True
	'''
	#return (player_y - next_y <= 1)
	return next_y > player_y -1

def is_miss_the_goal(next_y, goal_y):
	''' if next_state passes the goal state, return True'''
	return next_y > goal_y

def get_state_cost(pos, node):
	'''
		return a higher cost if the moves is diagonal
	'''
	if pos[1] > node[1] and pos[0] != node[0]:
		return 1.2
	return 1



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

#A* with 3 heuristics: 
	# 1.distance to point
	# 2. check if it's passed the point vertically
	# 3. check if it's stalling on a platform

def analyze_specific(thing, goal):
	startTime = time.time()
	tempDesign = copy.deepcopy(thing)
	sim = Simulator(tempDesign)
	init = sim.get_initial_state()

	path = []

	ANALYSIS = {init: None}

	startingNode = (init[0], init[1], 0) # (x,y), ability, turn)
	
	ANALYSIS[startingNode] = None

	q = [(0, init[0], init[1], 0, tempDesign, sim)] # distance from start, (point), abilities, turn number, newDesign) 

	while q:
		node = heappop(q)
		#print (node[1], node[2], int(node[3] / turns_to_move))
		#Node structure: (distance from start, (point), abilities, turn number, newDesign) 

		# not an exhaustive search, so stop as soon as you find the goal platform, which moves
		tempGoal = (goal[0], goal[1] - turns_number(node[3]) ) 

		if node[1] == tempGoal:
			currNode = (node[1], node[2], turns_number(node[3]))

			# build path
			while ANALYSIS[currNode] != None:
				# print currNode
				path.append(currNode[0])
				currNode = ANALYSIS[currNode]
			break

		# simulate first, THEN check the moves so that we don't get invalid moves
		tempSim = Simulator(node[4])
		moves = tempSim.get_moves()

		#see all possible states for each move
		states = []
		for move in moves:
			if tempSim.get_next_state((node[1],node[2]), move) != None:
				pos, abil = tempSim.get_next_state((node[1], node[2]), move)
				
				tempResult = p6_tool.take_turn(copy.deepcopy(node[4]), node[3], pos)

				#check if it's moved diagonally downward and add distance accordingly
				cost = get_state_cost(pos, node[1]) 

				#print " -- ", tempResult[1]['specials'].keys()[0]					
				newState = (node[0] + cost, tempResult[1]['specials'].items()[0][0], abil, tempResult[0], tempResult[1])
				states.append(newState)

		#Use ANALYSIS like a prev dict, only each key now has states so the solution will be unique for each set of abilities 
		for state in states:
			
			# ignore nodes that are stalling; they already have no valid path
			if is_falling(init[0][1], state[1][1]) and not is_miss_the_goal(state[1][1], tempGoal[1]):

				curr = (state[1], state[2], turns_number(state[3]))
				tent_score = state[0] + distance_heuristic(state[1], tempGoal)

				if (curr not in ANALYSIS or tent_score < node[0]) :
					#need to make nodes contain data on design movements or else they can't move to the same place twice
					ANALYSIS[curr] = (node[1], node[2], turns_number(node[3]))
					state = (tent_score, state[1], state[2], state[3], state[4])
					heappush(q, state)

	print "Time taken: ", time.time() - startTime
	return path

def distance_heuristic(goal, curr):
	dist = math.sqrt(((goal[0] - curr[0]) * (goal[0] - curr[0])) + ((goal[1] - curr[1]) * (goal[1] - curr[1])))
	return dist


def draw_path(path, draw_line, turn_num):	
	temp_turn = turn_num
	index = len(path) - 1
	color = p6_tool.make_color1()
	offset = (0,0)
	while index > 0:
		temp_turn += 1
		if temp_turn % turns_to_move is 0:
			color = p6_tool.make_color2()
		else:
			color = p6_tool.make_color1()
		curr = path[index]
		draw_line(curr, path[index-1], offset, color)
		index = index - 1
		curr = path[index-1]
	