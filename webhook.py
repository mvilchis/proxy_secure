from flask import request, url_for, current_app, make_response
from flask_api import FlaskAPI, status, exceptions
from flask import jsonify,Response
import os, ast, json, requests
from datetime import timedelta

from functools import update_wrapper

app = FlaskAPI(__name__)
TOKEN_MISALUD = os.getenv('TOKEN_MISALUD', "")
TOKEN_RP = os.getenv('TOKEN_RP', "")
RP_URL= os.getenv('RP_URL', "")

def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator



@app.route('/', methods=['GET','POST'])
@crossdomain(origin='*')
def secure_proxy(name=None):
    name = request.args.get('name')
    urns = request.args.get('urns')
    contacts = request.args.get("contacts")
    flow = request.args.get("flow")
    type_operation = request.args.get('type_operation')
    token = request.args.get('token')
    if token != TOKEN_MISALUD:
        return json.dumps({ "error": "error" }), 400
    if type_operation == "create_contact":
        token = 'token %s' % TOKEN_RP
        url = 'https://rapidpro.datos.gob.mx/api/v2/contacts.json'
        headers = {'content-type': 'application/json', 'Authorization': token}
        payload = { "urns": [urns]}
        r = requests.post(url, data = json.dumps(payload), headers=headers)
        if r.ok:
           return {"uuid": r.json()["uuid"]}
    if type_operation == "get_contact":
        token = 'token %s' % TOKEN_RP
        url = 'https://rapidpro.datos.gob.mx/api/v2/contacts.json'
        headers = {'content-type': 'application/json', 'Authorization': token}
        payload = {"urn":urns}
        r = requests.get(url, params = payload, headers=headers)
        if r.ok:
           return {"uuid": r.json()["results"][0]["uuid"]}
    if type_operation == "star_conversation":
        token = 'token %s' % TOKEN_RP
        payload={"backend":"Telcel",
                "sender":contacts,
                "ts":"1",
                "id":"758af0a175f8a86"}
        if flow == "20308c47-002a-446c-a4f8-a21482f66bc8":
            #Reinscription
            payload["message"] = "reinscription"
        else:
            #First time
            payload["message"] = "altagobmx"
        r = requests.get(RP_URL, params = payload)
        if r.ok:
            return json.dumps({"request":"done"})

    return json.dumps({ "error": "error" }), 400


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.run(debug=True,host="0.0.0.0", port= int(os.getenv('WEBHOOK_PORT', 5000)))
