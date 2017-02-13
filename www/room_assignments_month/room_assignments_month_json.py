import json
import room_assignments_month as room_assignments_month


def get_json_response(cfg):
	results = room_assignments_month.main(cfg)

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
		for group in variable_matrix:
			for row in group:
				for cell in row:
					response['variables'][cell.name()]= cell.solution_value()
					if (cell.solution_value()==1):
						meeting_room = cell.name().split(' in room ')
						meeting_day = meeting_room[0].split(': ')
						day = meeting_day[0]
						client = meeting_day[1]
						room = meeting_room[1]
						if day not in response['variables_display']:
							 response['variables_display'][day] = dict()
						response['variables_display'][day][room]= client
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


