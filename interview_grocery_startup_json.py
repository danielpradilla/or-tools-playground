#interview_grocery_startup_json.py

import json
import interview_grocery_startup as igs


def get_json_response(cfg, what):
	results = igs.main(cfg, what)

	solver = results['solver']


	if results['result_status'] == solver.OPTIMAL:
		response = {'result_status': 'optimal answer'}

		variable_list = results['variable_list']

		print solver.wall_time()
		print solver.Objective().Value()

		response['wall_time'] = solver.wall_time()
		response['objective_value']= solver.Objective().Value()

		response['variables'] = dict()

		response['variables_sum']=0
		for variable in variable_list:
			response['variables'][variable.name()]= variable.solution_value()
			response['variables_sum']+=variable.solution_value()

	elif results['result_status'] == solver.INFEASIBLE:
   		response = {'result_status': 'infeasible'}
  	elif results['result_status'] == solver.POSSIBLE_OVERFLOW:
		response = {'result_status': 'overflow'}

	json_response = json.dumps(response, sort_keys=True)

	return json_response

def main(cfg, what):
	json_response = get_json_response(cfg, what)
	print(json_response)
	return json_response


if __name__ == '__main__':
	cfg = {'maxWeight': 10,
		'maxCost': 100,
		'minCals': 14000,
		'minShop': 4/16.0, #16 ounces per pound
		'food':  [['ham',650, 4],
					['lettuce',70,1.5],
					['cheese',1670,5],
					['tuna',830,20],
					['bread',1300,1.20]]
	}

	main(cfg, 'cost')


