import json
import logging
import machine

from utils import files
from lib.microdot import Microdot, send_file, Request, Response
from data.user_config import UserConfig
from services.service_manager import service_locator
from services.user_service import UserService
from services.fan_service import FanService
from services.bluetooth_receive_service import BluetoothReceiveService

app = Microdot()

@app.route('/', methods=['GET', 'POST'])
async def root(request):
    if request.method == 'GET':
        return send_file('../web/configuration.html')
    elif request.method == 'POST':
        logging.debug("[WebServer] : Json Request - {0}".format(request.json))
        
        # Process the form data
        user_config = UserConfig()
        hr_value = 0
        for i in range(0, 4):
            try:
                hr_value = int(request.json[i]['hr'])
            except:
                hr_value = 0
            
            user_config.add_fan_mode(
                i+1,
                request.json[i]['en'] == True, 
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


@app.route('scan', methods=['GET'])
async def scan_bluetooth(request):
    await service_locator.get(BluetoothReceiveService).disconnect()
    service_locator.get(BluetoothReceiveService).set_state(BluetoothReceiveService._STATE_SCANNING)


@app.route('reset', methods=['GET'])
async def reset(request):
    logging.debug("[WebServer] : System Restart Requested")
    machine.reset()


@app.route('relay', methods=['GET'])
async def set_relay(request):
    if request.args is not None:
        logging.debug("[WebServer] : Request Args - {0}".format(request.args))
        logging.debug("[WebServer] : Updated Relay - {0}, {1}".format(int(request.args['id'][0]), bool(int(request.args['status'][0]))))
        if int(request.args['id'][0]) == 0:
            service_locator.get(FanService).disable_all_relays()
            service_locator.get(FanService).change_fan_mode(FanService.__MODE_HEARTRATE)
        else:
            service_locator.get(FanService).change_fan_mode(FanService.__MODE_MANUAL)
            service_locator.get(FanService).set_relay_by_id(int(request.args['id'][0]), bool(int(request.args['status'][0])))  
    return Response()