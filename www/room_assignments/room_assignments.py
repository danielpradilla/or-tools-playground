"""
Below is the information of the rooms available on a particular day and the meetings that need to be assigned to rooms

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

Each meeting should be assigned to one room
Each room can fit only one meeting
Each room capacity must match or exceed the number of attendees


Goal: optimize the usage of meeting rooms. Avoid assinging meetings with small attendees to large rooms.




"""

from __future__ import division
from ortools.linear_solver import pywraplp

def configure_variables(cfg, solver):
	#variable_matrix will be a matrix of variables following the pattern [meeting_i][room_j]
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	if (len(meetings)>len(rooms)):
		variable_matrix = [[0 for i in range(len(meetings))] for j in range(len(rooms))]
	else:
		variable_matrix = [[0 for i in range(len(rooms))] for j in range(len(meetings))]		
	variable_list = []
	for i in range(0, len(meetings)):
		for j in range(0, len(rooms)):
			variable_name = str('%s in room %s' %(meetings[i][1],rooms[j][0]))
			variable_list.append(solver.NumVar(0, 1, variable_name) )
			variable_matrix[i][j]=variable_list[-1]

	return variable_matrix


def configure_constraints(cfg, solver, variable_matrix):
	constraint_list=[]
	meetings = cfg['meetings']
	rooms = cfg['rooms']

	#one meeting per client
	#sum of all the meetings per client = 1
	for i in range(0, len(meetings)):
		constraint_list.append(solver.Constraint(1,1))
		for j in range(0, len(rooms)):
			constraint_list[-1].SetCoefficient(variable_matrix[i][j],1)

	#no two meetings in the same room
	#sum of all the meetings per room = 1
	for j in range(0, len(rooms)):
		constraint_list.append(solver.Constraint(0,1))
		for i in range(0, len(meetings)):
			constraint_list[-1].SetCoefficient(variable_matrix[i][j],1)

	#no meetings in room under capacity
	#sum of all the meetings where attendance > capacity = 0
	for j in range(0, len(rooms)):
		constraint_list.append(solver.Constraint(0,0))
		for i in range(0, len(meetings)):
			if (meetings[i][2] > rooms[j][1]):
				constraint_list[-1].SetCoefficient(variable_matrix[i][j],1)
	
	return constraint_list


def configure_objective(cfg, solver, variable_matrix, constraint_list):
	
	meetings = cfg['meetings']
	rooms = cfg['rooms']

	objective = solver.Objective()
	
	what = cfg['what']
	
	# Define our objective: minimize the ratio capacity / attendees
	for i in range(0, len(meetings)):
		for j in range(0, len(rooms)):
			objective.SetCoefficient(variable_matrix[i][j], (rooms[j][1]/meetings[i][2]) )

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
		for row in variable_matrix:
			for cell in row:
				print(('%s = %f' % (cell.name(), cell.solution_value())))
				var_sum+=cell.solution_value()
		print(('Variable sum = %f' % var_sum));

		print('Advanced usage:')
		print(('Problem solved in %d iterations' % solver.iterations()))

		for row in variable_matrix:
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
					['II',22],
					['III',198],
					['IV',61]],
			'meetings':  [[1,'UNHCR', 50],
							[2,'Town Hall', 150],
							[3,'UNCTAD', 68],
							[4,'CAT', 15]]
		}

	main(cfg)
