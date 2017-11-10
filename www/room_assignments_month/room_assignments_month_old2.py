"""
Linera programming example for 1 month period
Each meeting has attendance and interpretation requirements
Each room has capacity and interpretation booths

Schedule is divided in days / slot / position within the slot
For example 17001203 or 17 001 2 03 is (from right to left) the third position on the second slot of the first day of year 17

"""

from __future__ import division
from ortools.linear_solver import pywraplp
import json
import time
import itertools

def configure_variables(cfg, solver):
	#variable_matrix will be a matrix of variables following the pattern [day_slot_position_h][meeting_i][room_j]
	print "---start configure_variables ---"
	start_time = time.time()
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']

	print (len(rooms), len(meetings), len(schedule), len(rooms)*len(meetings)*len(schedule))
	# comprehension
	# [day/slot][meetings][rooms][position]
	# variable_matrix = [
	# 					[
	# 						[ 
	# 							[solver.NumVar(0, 1, str('day/slot/position %s: %s in room %s' %(str(m).zfill(2).join(schedule[h]['slot']), get_meeting_id(meetings[i]), get_room_code(rooms[j])) ) ) for m in range(1, schedule[h]['meetings'][meetings[i]['MMMMM']])] 
	# 							for j in range(len(rooms)) if schedule[h]['meetings'][meetings[i]['MMMMM']]>0 and meetings[i]['MEETING_PARTICIPANTS'] <= rooms[j]['NumberOfSeats'] and meetings[i]['INT_LANGUAGES_NUM'] <= rooms[j]['NumberOfBooths'] 
	# 						] for i in range(len(meetings))
	# 					] for h in range(len(schedule))
	# 				]	
	variable_matrix = [[[None for j in range(len(rooms))] for i in range(len(meetings))] for h in range(len(schedule))]
	print("---create empty variable matrix %s seconds ---" % (time.time() - start_time))
	# variable_list = [None for x in range(len(rooms) * len(meetings) * len(schedule))]
	# variable_list = []
	print("---create empty variable list %s seconds ---" % (time.time() - start_time))


	#print variable_matrix
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			for j in range(0, len(rooms)):
				number_of_meetings = schedule[h]['meetings'][meetings[i]['MMMMM']]
				if number_of_meetings>0 and meetings[i]['MEETING_PARTICIPANTS'] <= rooms[j]['NumberOfSeats'] and meetings[i]['INT_LANGUAGES_NUM'] <= rooms[j]['NumberOfBooths']:
							variable_matrix[h][i][j] = []
							for m in range(1, number_of_meetings):
								slot = str(m).zfill(2).join(schedule[h]['slot'])
								variable_name = str('day/slot/position %s: %s in room %s' %(slot, get_meeting_id(meetings[i]), get_room_code(rooms[j]) ) )
								variable = solver.NumVar(0, 1, variable_name)
								variable_matrix[h][i][j].append(variable)
					## print variable_name
		## print (100 * h/len(schedule))

	print("---configure_variables %s seconds ---" % (time.time() - start_time))
	return variable_matrix


def configure_constraints(cfg, solver, variable_matrix):
	print "---start configure_constraints ---"	
	start_time = time.time()
	constraint_list=[]
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']


	#one meeting per slot, when they have scheduled meetings
	#sum of all the meetings per slot, when they have schedules = 1
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			#the value of the constraint is in the MMMMM key of the meetings dict in each row of the schedule 
			#[{slot: slot1, meetings:{meeting_1: 1, meeting_2:0..}}, {slot: slot2, meetings:{meeting_1: 1, meeting_2:0..}}]
			value = schedule[h]['meetings'][meetings[i]['MMMMM']]
			if (value>0):
				value=1
			constraint_list.append(solver.Constraint(value,value))
			for j in range(0, len(rooms)):
				if variable_matrix[h][i][j] is not None:
					for m in variable_matrix[h][i][j]:
						constraint_list[-1].SetCoefficient(m,1)
		# print (100 * h/len(schedule))

	# #no two meetings in the same room, per slot
	# #sum of all the meetings per room = 1
	# for h in range(0, len(schedule)):
	# 	for j in range(0, len(rooms)):
	# 		constraint_list.append(solver.Constraint(0,1))
	# 		for i in range(0, len(meetings)):
	# 			if variable_matrix[h][i][j] is not None:
	# 				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)
	# 	print (100 * h/len(schedule))


	#implicit
	# #no meetings in room under capacity
	# #sum of all the meetings where attendance > capacity = 0
	# for h in range(0, len(schedule)):
	# 	for j in range(0, len(rooms)):
	# 		constraint_list.append(solver.Constraint(0,0))
	# 		for i in range(0, len(meetings)):
	# 			if (meetings[i]['MEETING_PARTICIPANTS'] > rooms[j]['NumberOfSeats']):
	# 				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)
	

	#implicit
	# #no meetings in room under interpretation capacity
	# #sum of all the meetings where attendance > capacity = 0
	# for h in range(0, len(schedule)):
	# 	for j in range(0, len(rooms)):
	# 		constraint_list.append(solver.Constraint(0,0))
	# 		for i in range(0, len(meetings)):
	# 			if (meetings[i]['INT_LANGUAGES_NUM'] > rooms[j]['NumberOfBooths']):
	# 				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)


	# #Meetings spanning multiple days on the same slot/position, should be assigned to the same room
	# #if a meeting is scheduled, then it should be scheduled in the same room for the next day/slot/position
	# #difference in meetings for the client in the same room should be 0
	# # day_1/slot_1: meeting_1 in room I  - day_2/slot_1: meeting_1 in room I = 0
	# # day_1/slot_1: meeting_1 in room II - day_2/slot_1: meeting_1 in room II = 0
	# # so, enforce that they are both 1 or they are both 0 in the matrix
	# for h in range(0, len(schedule)):
	# 	for i in range(0, len(meetings)):
	# 		for j in range(0, len(rooms)):
	# 			if variable_matrix[h][i][j] is not None:
	# 				#if you are in record 2 of the schedule list, start to compare
	# 				if (h>0):
	# 					#if the meeting is scheduled in the same slot as it was the day before
	# 					if (schedule[h]['meetings'][meetings[i]['MMMMM']]==1 and schedule[h-1]['meetings'][meetings[i]['MMMMM']]==1):
	# 						constraint_list.append(solver.Constraint(0,0))
	# 						constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)
	# 						constraint_list[-1].SetCoefficient(variable_matrix[h-1][i][j],-1)
	# 	print (100 * h/len(schedule))

	print("---configure_constraints %s seconds ---" % (time.time() - start_time))
	return constraint_list


def configure_objective(cfg, solver, variable_matrix):
	print "---start configure_objective ---"
	start_time = time.time()
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']

	objective = solver.Objective()

	what = cfg['what']

	# Define our objective: minimize the ratio capacity / attendees for the totality of each meeting
	# in other words, minimize the sum of the cost of all the meetings scheduled for each client/room
	# the coefficient matrix is just for testing. Contains the total cost of holding a meeting of a client in one room
	coefficient_matrix = [[0 for i in range(len(rooms))] for j in range(len(meetings))]
	for h in range(0, len(schedule)):
		for i in range(0, len(meetings)):
			for j in range(0, len(rooms)):
				coefficient_matrix[i][j] = rooms[j]['NumberOfSeats'] / meetings[i]['MEETING_PARTICIPANTS']
				if schedule[h]['meetings'][meetings[i]['MMMMM']]>0 and meetings[i]['MEETING_PARTICIPANTS'] <= rooms[j]['NumberOfSeats'] and meetings[i]['INT_LANGUAGES_NUM'] <= rooms[j]['NumberOfBooths']:
					#print(h, i, j)
					if variable_matrix[h][i][j] is not None:
						for m in variable_matrix[h][i][j]:
							#print(m)
							objective.SetCoefficient(m, (rooms[j]['NumberOfSeats'] / meetings[i]['MEETING_PARTICIPANTS'] ) )
		# print (100 * i / len(meetings))

	# print ('coefficient_matrix',coefficient_matrix)

	objective.SetMinimization()
	print("---configure_objective %s seconds ---" % (time.time() - start_time))

	return objective


def solve(solver):
	print "---start solve ---"
	start_time = time.time()
	result_status = solver.Solve()
	print("---solve %s seconds ---" % (time.time() - start_time))
	return result_status


def print_solution(solver,result_status,variable_matrix,constraint_list):

	if result_status == solver.OPTIMAL:
		print('Successful solve.')
		# The problem has an optimal solution.
		print(('Problem solved in %f milliseconds' % solver.wall_time()))
		# The objective value of the solution.
		print(('Optimal objective value = %f' % solver.Objective().Value()))
		# The value of each variable in the solution.
		var_sum = 0
		# print variable_matrix
		for group in variable_matrix:
			for row in group:
				for cell in row:
					if cell is not None:
						for sub_cell in cell:
							print(('%s = %f' % (sub_cell.name(), sub_cell.solution_value())))
							var_sum+=sub_cell.solution_value()
		# print(('Variable sum = %f' % var_sum))

		# print('Advanced usage:')
		# print(('Problem solved in %d iterations' % solver.iterations()))

		# for group in variable_matrix:
		# 	for row in group:
		# 		for cell in row:
		# 			if cell is not None:
		# 				print(('%s: reduced cost = %f' % (cell.name(), cell.reduced_cost())))

		# activities = solver.ComputeConstraintActivities()
		# for i, constraint in enumerate(constraint_list):
		# 	print(('constraint %d: dual value = %f\n'
		#       '               activity = %f' %
		#       (i, constraint.dual_value(), activities[constraint.index()])))

	elif result_status == solver.INFEASIBLE:
   		print('No solution found.')
  	elif result_status == solver.POSSIBLE_OVERFLOW:
		print('Some inputs are too large and may cause an integer overflow.')

def main(cfg):
	start_time = time.time()
	solver = pywraplp.Solver('SolveSimpleSystem',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

	variable_matrix = configure_variables(cfg, solver)

	objective = configure_objective(cfg, solver, variable_matrix)

	constraint_list = configure_constraints(cfg, solver, variable_matrix)

	result_status = solve(solver)

	print_solution(solver, result_status, variable_matrix, constraint_list)

	print("---total execution %s seconds ---" % (time.time() - start_time))

	return {'variable_matrix':variable_matrix, 
			'constraint_list': constraint_list, 
			'objective':objective, 
			'solver':solver, 
			'result_status': result_status}


def load_json_from_file(path):
	with open(path) as json_data:
		data = json.load(json_data)
	return data	


def create_rooms_list(rooms):
	selected_rooms = filter(lambda r: r['Selected']==1, rooms)
	rtn = sorted(selected_rooms, key = lambda k: (k['Venue'], k['Name']) ) 
	return rtn


def get_room_code(room):
	return str('%s - %s' %(room['Venue'],room['RoomNumber']) )


def create_meetings_list(meetings):
	for meeting in meetings:
		# convert some of the fields to numeric
		for field in ['INT_LANGUAGES_NUM','MEETING_PARTICIPANTS']:
			meeting[field] = int(meeting[field])
	rtn = sorted(meetings, key = lambda k: (k['MMMMM']) ) 
	return rtn


def get_meeting_id(meeting):
	return meeting['YYDDDMMMMMSAA']


def get_meeting_code(meeting):
	return meeting['MMMMM']


def get_slot_code(meeting):
	# return meeting['YYDDSAA']
	# return meeting['S'] + meeting['AA'] + meeting['YYDDD']
	return meeting['S'] + meeting['YYDDD']


def create_schedule_matrix(meetings):
	#creates a schedule list
	#each element contains an object with properties slot and meetings
	#meetings is a dict with each meeting code as key and value indicating if meeting is scheduled {meeting_1: 1, meeting_2:0..}
	#[{slot: slot1, meetings:{meeting_1: 1, meeting_2:0..}}, {slot: slot2, meetings:{meeting_1: 1, meeting_2:0..}}]
	start_time = time.time()
	schedule = []
	all_slots = []
	all_meetings = []

	all_slots = sorted(set(map(get_slot_code, meetings)))
	all_meetings = set(map(get_meeting_code, meetings))

	# build a schedule of slots and meetings with all the meetings set to 0
	for slot in all_slots:
		schedule.append({'slot': slot, 'meetings': dict.fromkeys(all_meetings, 0)})

	# change the meeting to 1 when a meeting is scheduled
	selected_meetings = filter(lambda m: int(m['SELECTED']) == 1, meetings)
	for meeting in selected_meetings:
		#get the position of the current meeting in the all_slots list
		h = all_slots.index(get_slot_code(meeting))
		schedule[h]['meetings'][meeting['MMMMM']] += 1

	# print sorted(schedule.keys())
	# print map(lambda s: s['slot'], schedule)
	# print schedule[-1]

	print("---create_schedule_matrix %s seconds ---" % (time.time() - start_time))
	return schedule


if __name__ == '__main__':
	cfg = {'what': 'space',
			'rooms': [],
			'meetings': [],
			'schedule': []
		}
	rooms = load_json_from_file('data/rooms.json')
	cfg['rooms'] = create_rooms_list(rooms)
	meetings = load_json_from_file('data/meetings.json')
	cfg['meetings'] = create_meetings_list(meetings)
	cfg['schedule'] = create_schedule_matrix(meetings)
	main(cfg)
