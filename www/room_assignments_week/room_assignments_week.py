"""
Below is the information of the rooms available for a 5-day work week and the meetings that need to be held throgout

room	capacity
I	71
II	22
III	198
IV	61

meeting	name	attendees
1	UNHCHR	50
2	Town Hall	150
3	UNCTAD	68
4	CAT	15
5	CERD	70

schedule of meetings
days 		Meetings
		1	2	3	4	5
1		X	X
2		X	X	X	X
3		X		X	X	X
4		X		X	X	X
5		X		X		X


Each meeting should be assigned to one room
Each room can fit only one meeting
Each room capacity must match or exceed the number of attendees
Meeting spanning multiple days should be assigned to the same room each day

Goal: optimize the usage of meeting rooms. Avoid assinging meetings with small attendees to large rooms.




"""

from __future__ import division
from ortools.linear_solver import pywraplp

def configure_variables(cfg, solver):
	#variable_matrix will be a matrix of variables following the pattern [meeting_i][room_j]
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']

	if (len(meetings)>len(rooms)):
		variable_matrix = [[[0 for i in range(len(meetings))] for j in range(len(rooms))] for h in range(len(schedule))]
	else:
		variable_matrix = [[[0 for i in range(len(rooms))] for j in range(len(meetings))] for h in range(len(schedule))]		
	
	variable_matrix = [[[0 for i in range(len(rooms))] for j in range(len(meetings))] for h in range(len(schedule))]		
	variable_list = []
	# print variable_matrix
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			for j in range(0, len(rooms)):
				variable_name = str('day %s: %s in room %s' %(schedule[h][0],meetings[i][1],rooms[j][0]))
				variable_list.append(solver.NumVar(0, 1, variable_name) )
				# print (h, i, j)
				# print variable_matrix
				variable_matrix[h][i][j]=variable_list[-1]

	return variable_matrix


def configure_constraints(cfg, solver, variable_matrix):
	constraint_list=[]
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']


	#one meeting per client, when they have scheduled meetings
	#sum of all the meetings per client, when they have schedules = 1
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			#the value of the constraint is index 2 of the schedule (index 1) for the day and the meeting (ie [1, [1,'client',0<--]])
			value = schedule[h][1][i][2]
			constraint_list.append(solver.Constraint(value,value))
			for j in range(0, len(rooms)):
				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)

	#no two meetings in the same room, per day
	#sum of all the meetings per room = 1
	for h in range(0, len(schedule)):
		for j in range(0, len(rooms)):
			constraint_list.append(solver.Constraint(0,1))
			for i in range(0, len(meetings)):
				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)

	#no meetings in room under capacity
	#sum of all the meetings where attendance > capacity = 0
	for h in range(0, len(schedule)):
		for j in range(0, len(rooms)):
			constraint_list.append(solver.Constraint(0,0))
			for i in range(0, len(meetings)):
				if (meetings[i][2] > rooms[j][1]):
					constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)
	

	#Meetings spanning multiple days should be assigned to the same room
	#if a meeting is scheduled, then it should be scheduled in the same room for the next day
	#difference in meetings for the client in the same room should be 0
	# day 1: UNHCR in room I  - day 2: UNHCR in room I = 0
	# day 1: UNHCR in room II - day 2: UNHCR in room II = 0
	# so, enforce that they are both 1 or they are both 0 in the matrix
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			for j in range(0, len(rooms)):
				if (h > 0 and schedule[h][1][i][2]==1 and schedule[h-1][1][i][2]==1):
					constraint_list.append(solver.Constraint(0,0))
					# print ('pairs', variable_matrix[h-1][i][j], variable_matrix[h][i][j])
					constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)
					constraint_list[-1].SetCoefficient(variable_matrix[h-1][i][j],-1)

	return constraint_list


def configure_objective(cfg, solver, variable_matrix, constraint_list):
	
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']

	objective = solver.Objective()
	
	what = cfg['what']
	
	# Define our objective: minimize the ratio capacity / attendees for the totality of each meeting
	# in other words, minimize the sum of the cost of all the meetings scheduled for each client/room
	# the coefficient matrix is just for testing. Contains the total cost of holding a meeting of a client in one room
	coefficient_matrix = [[0 for i in range(len(rooms))] for j in range(len(meetings))]
	for i in range(0, len(meetings)):
		for j in range(0, len(rooms)):
			for h in range(0, len(schedule)):
				coefficient_matrix[i][j]=rooms[j][1]/meetings[i][2]
				objective.SetCoefficient(variable_matrix[h][i][j], (rooms[j][1]/meetings[i][2]) * schedule[h][1][i][2] )

	# print ('coefficient_matrix',coefficient_matrix)

	objective.SetMinimization()

	return objective


def solve(solver):
	result_status = solver.Solve()
	return result_status

def print_solution(solver,result_status,variable_matrix,constraint_list):

	if result_status == solver.OPTIMAL:
		print('Successful solve.')
		# The problem has an optimal solution.
		print(('Problem solved in %f milliseconds' % solver.wall_time()))
		# The objective value of the solution.
		print(('Optimal objective value = %f' % solver.Objective().Value()))
		# The value of each variable in the solution.
		var_sum=0
		for group in variable_matrix:
			for row in group:
				for cell in row:
					print(('%s = %f' % (cell.name(), cell.solution_value())))
					var_sum+=cell.solution_value()
		print(('Variable sum = %f' % var_sum));

		print('Advanced usage:')
		print(('Problem solved in %d iterations' % solver.iterations()))

		for group in variable_matrix:
			for row in group:
				for cell in row:
					print(('%s: reduced cost = %f' % (cell.name(), cell.reduced_cost())))
		
		activities = solver.ComputeConstraintActivities()
		for i, constraint in enumerate(constraint_list):
			print(('constraint %d: dual value = %f\n'
		      '               activity = %f' %
		      (i, constraint.dual_value(), activities[constraint.index()])))

	elif result_status == solver.INFEASIBLE:
   		print('No solution found.')
  	elif result_status == solver.POSSIBLE_OVERFLOW:
		print('Some inputs are too large and may cause an integer overflow.')

def main(cfg):

	solver = pywraplp.Solver('SolveSimpleSystem',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

	variable_matrix = configure_variables(cfg, solver)

	constraint_list = configure_constraints(cfg, solver, variable_matrix)

	objective = configure_objective(cfg, solver, variable_matrix, constraint_list)

	result_status = solve(solver)

	print_solution(solver, result_status, variable_matrix, constraint_list)

	return {'variable_matrix':variable_matrix, 
			'constraint_list': constraint_list, 
			'objective':objective, 
			'solver':solver, 
			'result_status': result_status}

if __name__ == '__main__':


	cfg = { 'what': 'space',
			'rooms': [['I',71],
					['II',60],
					['III',198],
					['IV',61]],
			'meetings':  [[1,'UNHCR', 50],
							[2,'Town Hall', 150],
							[3,'UNCTAD', 68],
							[4,'CAT', 15],
							[5,'CERD', 70]],
			#schedule has the form [day, [[meeting, client hasmeeting], [meeting, client, hasmeeting]]]
			'schedule':	[[1, [[1,'UNHCR', 1],[2,'Town Hall', 1],[3,'UNCTAD', 0],[4,'CAT', 0],[5,'CERD', 0]]],
						 [2, [[1,'UNHCR', 1],[2,'Town Hall', 1],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 0]]],
						 [3, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 1]]],
						 [4, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 1],[5,'CERD', 1]]],
						 [5, [[1,'UNHCR', 1],[2,'Town Hall', 0],[3,'UNCTAD', 1],[4,'CAT', 0],[5,'CERD', 1]]]]
		}

	main(cfg)
