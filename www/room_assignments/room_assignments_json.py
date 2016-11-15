#interview_grocery_startup_json.py

import json
import room_assignments as room_assignments


def get_json_response(cfg):
	results = room_assignments.main(cfg)

	solver = results['solver']


	if results['result_status'] == solver.OPTIMAL:
		response = {'result_status': 'optimal answer'}

		variable_matrix = results['variable_matrix']

		print solver.wall_time()
		print solver.Objective().Value()

		response['wall_time'] = solver.wall_time()
		response['objective_value']= solver.Objective().Value()

		response['variables'] = dict()

		response['variables_display'] = dict()

		response['variables_sum']=0
		for row in variable_matrix:
			for cell in row:
				response['variables'][cell.name()]= cell.solution_value()
				if (cell.solution_value()==1):
					meeting_room = cell.name().split(' in ')
					response['variables_display'][meeting_room[0]] = meeting_room[1]
				response['variables_sum']+=cell.solution_value()

	elif results['result_status'] == solver.INFEASIBLE:
   		response = {'result_status': 'infeasible'}
  	elif results['result_status'] == solver.POSSIBLE_OVERFLOW:
		response = {'result_status': 'overflow'}

	json_response = json.dumps(response, sort_keys=True)

	return json_response

def main(cfg):
	json_response = get_json_response(cfg)
	print(json_response)
	return json_response


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


