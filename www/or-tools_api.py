# room_assignments_api.py

# requires falcon, gunicorn

import falcon
import json

from interview_grocery_startup import interview_grocery_startup_json as igsj 
from room_assignments import room_assignments_json as raj 
from room_assignments_week import room_assignments_week_json as rawj 


ALLOWED_ORIGINS = 'http://localhost'

class CorsMiddleware(object):
	def process_request(self, request, response):
		origin = request.get_header('Origin')
		if origin is not None and origin in ALLOWED_ORIGINS:
			response.set_header('Access-Control-Allow-Origin', origin)
		response.set_header('Access-Control-Allow-Origin', '*')


class InterviewGroceryStartupResource(object):
    def on_get(self, req, resp):
		#Handles GET requests
		resp.status = falcon.HTTP_200  # This is the default status
		resp.body =  igsj.main(cfg,cfg['what'])

    def on_post(self, req, resp):
		try:
			body = req.stream.read()
			body_json = json.loads(body.decode('utf-8'))
			print(body)
			cfg = body_json["cfg"]
		except KeyError:
			raise falcon.HTTPBadRequest(
			'Missing Config',
			'A config (cfg) must be submitted in the request body.')

		resp.status = falcon.HTTP_200
		resp.body = igsj.main(cfg,cfg['what'])


class APITools(object):
	#generic get function
	def get(object, module, self, req, resp):
		#Handles GET requests
		resp.status = falcon.HTTP_200  # This is the default status
		resp.body =  module.main(cfg)
		return resp

	def post(object, module, self, req, resp):
		try:
			body = req.stream.read()
			body_json = json.loads(body.decode('utf-8'))
			print(body)
			cfg = body_json["cfg"]
		except KeyError:
			raise falcon.HTTPBadRequest(
			'Missing Config',
			'A config (cfg) must be submitted in the request body.')

		resp.status = falcon.HTTP_200
		resp.body = module.main(cfg)
		return resp



class RoomAssignmentsResource(object):
    def on_get(self, req, resp):
    	resp = apitools.get(raj, self, req, resp)

    def on_post(self, req, resp):
		resp = apitools.post(raj, self, req, resp)

class RoomAssignmentsWeekResource(object):
    def on_get(self, req, resp):
    	resp = apitools.get(rawj, self, req, resp)

    def on_post(self, req, resp):
		resp = apitools.post(rawj, self, req, resp)


# falcon.API instances are callable WSGI apps
app = application = falcon.API(middleware=[CorsMiddleware()])

apitools = APITools()

# Resources are represented by long-lived class instances
igsapi = InterviewGroceryStartupResource()
room_assignments_api = RoomAssignmentsResource()
room_assignments_week_api = RoomAssignmentsWeekResource()

# ApiTestResource will handle all requests to the '/apitest' URL path
app.add_route('/igsapi', igsapi)
app.add_route('/room_assignments_api', room_assignments_api)
app.add_route('/room_assignments_week_api', room_assignments_week_api)



# Run as
#gunicorn or-tools_api -b :18000 --reload

