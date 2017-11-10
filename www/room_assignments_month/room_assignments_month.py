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


def configure_variables(cfg, solver):
	#variable_matrix will be a matrix of variables following the pattern [day_slot_position_h][meeting_i][room_j]
	print "---start configure_variables ---"
	start_time = time.time()
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']

	print (len(rooms), len(schedule), len(rooms)*len(schedule))

	variable_dictionary = dict()

	for j in range(0, len(rooms)):
		for h in range(0, len(schedule)):
			for meeting in schedule[h]['meetings']:
				# if meeting_fits_in_room(meeting, rooms[j]):
					variable_index = get_variable_index(meeting, rooms[j])
					variable_name = str('day/slot/position %s: %s in room %s' %(get_slot_position_code(meeting), get_meeting_id(meeting), get_room_code(rooms[j]) ) )
					variable = solver.NumVar(0, 1, variable_name)
					variable_dictionary[variable_index]=variable

	print("---configure_variables %s seconds ---" % (time.time() - start_time))
	return variable_dictionary


def configure_constraints(cfg, solver, variable_dictionary):
	print "---start configure_constraints ---"	
	start_time = time.time()
	constraint_list=[]
	meetings = cfg['meetings']
	rooms = cfg['rooms']
	schedule = cfg['schedule']


	#one meeting per slot, when they have scheduled meetings
	#sum of all the meetings per slot, when they have schedules = 1
	for h in range(0, len(schedule)):
		for meeting in schedule[h]['meetings']:
			constraint_list.append(solver.Constraint(1,1))
			for j in range(0, len(rooms)):
				# if meeting_fits_in_room(meeting, rooms[j]):
					variable_index = get_variable_index(meeting, rooms[j])
					variable = variable_dictionary[variable_index]
					constraint_list[-1].SetCoefficient(variable,1)

	#no two meetings in the same room, per slot
	#sum of all the meetings per room = 1
	for h in range(0, len(schedule)):
		for j in range(0, len(rooms)):
			constraint_list.append(solver.Constraint(0,1))
			for meeting in schedule[h]['meetings']:
				# if meeting_fits_in_room(meeting, rooms[j]):
					variable_index = get_variable_index(meeting, rooms[j])
					variable = variable_dictionary[variable_index]
					constraint_list[-1].SetCoefficient(variable,1)

	#no meetings in room under capacity
	#sum of all the meetings that do not fit in a room = 0
	for h in range(0, len(schedule)):
		for j in range(0, len(rooms)):
			constraint_list.append(solver.Constraint(0,0))
			for meeting in schedule[h]['meetings']:
				if not meeting_fits_in_room(meeting, rooms[j]):
					variable_index = get_variable_index(meeting, rooms[j])
					variable = variable_dictionary[variable_index]
					constraint_list[-1].SetCoefficient(variable,1)

	#implicit
	# #no meetings in room under interpretation capacity
	# #sum of all the meetings where attendance > capacity = 0
	# for h in range(0, len(schedule)):
	# 	for j in range(0, len(rooms)):
	# 		constraint_list.append(solver.Constraint(0,0))
	# 		for i in range(0, len(meetings)):
	# 			if (meetings[i]['INT_LANGUAGES_NUM'] > rooms[j]['NumberOfBooths']):
	# 				constraint_list[-1].SetCoefficient(variable_matrix[h][i][j],1)


	#Meetings spanning multiple days on the same slot/position, should be assigned to the same room
	#if a meeting is scheduled, then it should be scheduled in the same room for the next day/slot/position
	#difference in meetings for the client in the same room should be 0
	# day_1/slot_1: meeting_1 in room I  - day_2/slot_1: meeting_1 in room I = 0
	# day_1/slot_1: meeting_1 in room II - day_2/slot_1: meeting_1 in room II = 0
	# so, enforce that they are both 1 or they are both 0 in the matrix
	for h in range(0, len(schedule)):
		for meeting in schedule[h]['meetings']:
			for j in range(0, len(rooms)):
					#if you are in record 2 of the schedule list, start to compare
					if (h>0):
						#if the meeting is scheduled in the same slot as it was the day before
						#find a match
						prev_meeting = next((m for m in schedule[h-1]['meetings'] if m['MMMMM'] == meeting['MMMMM'] and m['AA'] == meeting['AA']), None)
						#create the constraint
						if prev_meeting:
							# print (get_meeting_id(meeting), get_meeting_id(prev_meeting))
							constraint_list.append(solver.Constraint(0,0))
							
							variable_index = get_variable_index(meeting, rooms[j])
							variable = variable_dictionary[variable_index]
							constraint_list[-1].SetCoefficient(variable,1)

							variable_index = get_variable_index(prev_meeting, rooms[j])
							variable = variable_dictionary[variable_index]
							constraint_list[-1].SetCoefficient(variable,-1)
	# 	print (100 * h/len(schedule))

	print("---configure_constraints %s seconds ---" % (time.time() - start_time))
	return constraint_list


def configure_objective(cfg, solver, variable_dictionary):
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
	for j in range(0, len(rooms)):
		for h in range(0, len(schedule)):
			for meeting in schedule[h]['meetings']:
				if meeting_fits_in_room(meeting, rooms[j]):
					variable_index = get_variable_index(meeting, rooms[j])
					variable = variable_dictionary[variable_index]
					objective.SetCoefficient(variable, (rooms[j]['NumberOfSeats'] / meeting['MEETING_PARTICIPANTS'] ) )

	objective.SetMinimization()
	print("---configure_objective %s seconds ---" % (time.time() - start_time))

	return objective


def solve(solver):
	print "---start solve ---"
	start_time = time.time()
	result_status = solver.Solve()
	print("---solve %s seconds ---" % (time.time() - start_time))
	return result_status


def print_solution(solver,result_status,variable_dictionary,constraint_list):

	if result_status == solver.OPTIMAL:
		print('Successful solve.')
		# The problem has an optimal solution.
		print(('Problem solved in %f milliseconds' % solver.wall_time()))
		# The objective value of the solution.
		print(('Optimal objective value = %f' % solver.Objective().Value()))
		# The value of each variable in the solution.
		var_sum = 0
		# print variable_dictionary
	
		for index, variable in variable_dictionary.iteritems():
			if variable.solution_value() > 0:
				print(('%s = %f' % (variable.name(), variable.solution_value())))
				var_sum+=variable.solution_value()
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

	variable_dictionary = configure_variables(cfg, solver)

	objective = configure_objective(cfg, solver, variable_dictionary)

	constraint_list = configure_constraints(cfg, solver, variable_dictionary)

	result_status = solve(solver)

	print_solution(solver, result_status, variable_dictionary, constraint_list)

	print("---total execution %s seconds ---" % (time.time() - start_time))

	return {'variable_dictionary':variable_dictionary, 
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
		for field in ['INT_LANGUAGES_NUM','MEETING_PARTICIPANTS','SELECTED']:
			meeting[field] = int(meeting[field])
	selected_meetings = filter(lambda m: m['SELECTED']==1, meetings)
	rtn = sorted(selected_meetings, key = lambda k: (k['MMMMM']) ) 
	return rtn


def get_meeting_id(meeting):
	return meeting['YYDDDMMMMMSAA']


def get_meeting_code(meeting):
	return meeting['MMMMM']


def get_slot_code(meeting):
	# return meeting['YYDDSAA']
	# return meeting['S'] + meeting['AA'] + meeting['YYDDD']
	return meeting['S'] + meeting['YYDDD']


def get_slot_position_code(meeting):
	return meeting['S'] + meeting['AA'] + meeting['YYDDD']


def get_variable_index(meeting, room):
	return str('%s|%s' %(get_meeting_id(meeting), get_room_code(room)) )


def meeting_fits_in_room(meeting, room):
	return meeting['MEETING_PARTICIPANTS'] <= room['NumberOfSeats'] and meeting['INT_LANGUAGES_NUM'] <= room['NumberOfBooths']


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
		schedule.append({'slot': slot, 'meetings': [meeting for meeting in meetings if get_slot_code(meeting) == slot ]})

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
	cfg['schedule'] = create_schedule_matrix(cfg['meetings'])
	main(cfg)
