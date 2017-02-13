# requires falcon, gunicorn

import falcon
import json
import room_assignments_month_json as rawj 


ALLOWED_ORIGINS = 'http://localhost'

class CorsMiddleware(object):
	def process_request(self, request, response):
		origin = request.get_header('Origin')
		if origin is not None and origin in ALLOWED_ORIGINS:
			response.set_header('Access-Control-Allow-Origin', origin)
		response.set_header('Access-Control-Allow-Origin', '*')

class RoomAssignmentsMonthResource(object):
    def on_get(self, req, resp):
		#Handles GET requests
		

		resp.status = falcon.HTTP_200  # This is the default status

		resp.body =  rawj.main(cfg)

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
		resp.body = rawj.main(cfg)



# falcon.API instances are callable WSGI apps
app = application = falcon.API(middleware=[CorsMiddleware()])

# Resources are represented by long-lived class instances
room_assignments_month_api = RoomAssignmentsMonthResource()

# ApiTestResource will handle all requests to the '/apitest' URL path
app.add_route('/room_assignments_month_api', room_assignments_month_api)

# Run as
#gunicorn room_assignments_month_api -b :18000 --reload

