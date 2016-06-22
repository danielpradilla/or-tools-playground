"""
So Tom, Dick & Harry showed up for an interview at the new grocery delivery startup.
There was a whiteboard, a laptop & a notebook, so they could use whatever makes them comfortable.

Tom's interview: The chief data scientist John Doe (JD) walked in.

JD. Lets talk about groceries.
Tom. Ok

You walk into a grocery store with a grocery bag and some cash, to buy groceries for a week.
 
1. your bag can hold ten pounds.
2. You have $100
3. You need about 2000 calories a day, so a weekly shopping trip is about 14,000 calories.
4. You must purchase at least 4 ounces of each grocery item.

Here's your dataset -

--- Calories Per Pound ---
Ham, 650 cals,
Lettuce, 70 cals
Cheese, 1670 cals
Tuna, 830 cals
Bread, 1300 cals
----

---- Price Per Pound ----
Ham, $4
Lettuce, $1.5
Cheese, $5
Tuna, $20
Bread, $1.20
----

Take your time, and list the number of ways you can buy your groceries.

JD walked out of the room.

Tom thought for a while.
Then he grabbed the laptop, opened up his favorite editor & wrote some code. When he was done - 


The rest of the story is here
http://www.jasq.org/just-another-scala-quant/new-agey-interviews-at-the-grocery-startup

"""

from ortools.linear_solver import pywraplp

maxWeight = 10
maxCost = 100
minCals = 14000
minShop = 4/16.0 #16 ounces per pound

#[name, calories, prices]
food =  [['ham',650, 4],
		['lettuce',70,1.5],
		['cheese',1670,5],
		['tuna',830,20],
		['bread',1300,1.20]]


def configure_variables(solver):
	variable_list = [[]] * len(food)
	for i in range(0, len(food)):
		#you must buy at least minShop of each
		variable_list[i] = solver.NumVar(minShop, solver.infinity(), food[i][0])

	return variable_list


def configure_constraints(solver, variable_list):
	#Define the constraints	
	constraint_list=[]
	#Constraint 1: totalWeight<maxWeight
	#ham + lettuce + cheese + tuna + bread <= maxWeight
	constraint_list.append(solver.Constraint(0, maxWeight))
	for i in range(0, len(food)):
		constraint_list[0].SetCoefficient(variable_list[i],1)

	#Constraint 2: totalPrice<=maxCost
	constraint_list.append(solver.Constraint(0, maxCost))
	for i in range(0, len(food)):
		constraint_list[1].SetCoefficient(variable_list[i],food[i][2])

	#Constraint 3: totalCalories>=minCals
	constraint_list.append(solver.Constraint(minCals, minCals + 100))
	for i in range(0, len(food)):
		constraint_list[2].SetCoefficient(variable_list[i],food[i][1])

	return constraint_list


def configure_objective(what, solver, variable_list, constraint_list):
	objective = solver.Objective()

	if (what=='cost'):
		# Define our objective: minimizing cost
		for i in range(0, len(food)):
			objective.SetCoefficient(variable_list[i], food[i][2])
		objective.SetMinimization()

	elif(what=='calories'):
		# Define our objective: maximizing calories
		for i in range(0, len(food)):
			objective.SetCoefficient(variable_list[i], food[i][1])
		objective.SetMaximization()

	elif(what=='fat-free'):
		# Define our objective: cutting on ham, cheese and tuna
		for i in range(0, len(food)):
			if (food[i][0] in ['ham','cheese','tuna']):
				objective.SetCoefficient(variable_list[i],1)
		objective.SetMinimization()
	else:
		# Define our objective: use all the money
		for i in range(0, len(food)):
			objective.SetCoefficient(variable_list[i], food[i][2])
		objective.SetMaximization()

	return objective


def solve(solver):
	result_status = solver.Solve()
	return result_status

def print_solution(solver,result_status,variable_list,constraint_list):

	if result_status == solver.OPTIMAL:
		print('Successful solve.')
		# The problem has an optimal solution.
		print(('Problem solved in %f milliseconds' % solver.wall_time()))
		# The objective value of the solution.
		print(('Optimal objective value = %f' % solver.Objective().Value()))
		# The value of each variable in the solution.
		for variable in variable_list:
			print(('%s = %f' % (variable.name(), variable.solution_value())))

		print('Advanced usage:')
		print(('Problem solved in %d iterations' % solver.iterations()))

		for variable in variable_list:
			print(('%s: reduced cost = %f' % (variable.name(), variable.reduced_cost())))
		
		activities = solver.ComputeConstraintActivities()
		for i, constraint in enumerate(constraint_list):
			print(('constraint %d: dual value = %f\n'
		      '               activity = %f' %
		      (i, constraint.dual_value(), activities[constraint.index()])))

	elif solve_status == assignment.INFEASIBLE:
   		print('No solution found.')
  	elif solve_status == assignment.POSSIBLE_OVERFLOW:
		print('Some inputs are too large and may cause an integer overflow.')


def main():

	solver = pywraplp.Solver('SolveSimpleSystem',pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

	variable_list = configure_variables(solver)
	constraint_list = configure_constraints(solver, variable_list)
	objective = configure_objective('cost', solver, variable_list, constraint_list)

	result_status = solve(solver)

	print_solution(solver, result_status, variable_list, constraint_list)

if __name__ == '__main__':
  main()
