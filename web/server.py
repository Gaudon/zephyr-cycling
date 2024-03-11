import json
import logging

from utils import files
from lib.microdot import Microdot, send_file, Request, Response
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.user_service import UserService
from services.fan_service import FanService

app = Microdot()

@app.route('/', methods=['GET', 'POST'])
async def root(request):
    if request.method == 'GET':
        return send_file('../web/configuration.html')
    elif request.method == 'POST':
        # Process the form data
        user_config = UserConfig()
        hr_value = 0
        for i in range(1, 9):
            try:
                hr_value = int(request.form.get("hr{0}".format(i)))
            except:
                hr_value = 0
            
            user_config.add_fan_mode(
                i,
                request.form.get("en{0}".format(i)) == 'on', 
                hr_value
            )

        file = open("config/user.json", "w")
        file.write(json.dumps(user_config.__dict__))
        file.close()

        # Notify the user service that the user settings have been changed.
        service_locator.get(UserService).update_user_config()


@app.route('config', methods=['GET'])
async def get_user_config(request):
    json_data = '{}'
    with open("../config/user.json", "r") as file:
        json_data = json.load(file)
        file.close()
    return json_data
    

@app.route('resources/<path:path>', methods=['GET'])
async def resources(request, path):
    if '..' in path:
        return 'Not found', 404
    return send_file('../web/resources/' + path, max_age=86400)


@app.route('relay', methods=['GET'])
async def set_relay(request):
    if request.args is not None:
        logging.debug("[WebServer] : Request Args - {0}".format(request.args))
        logging.debug("[WebServer] : Updated Relay - {0}, {1}".format(int(request.args['id'][0]), bool(int(request.args['status'][0]))))
        service_locator.get(FanService).change_fan_mode(FanService.__MODE_MANUAL)
        service_locator.get(FanService).set_relay_by_id(int(request.args['id'][0]), bool(int(request.args['status'][0])))  
    return Response()