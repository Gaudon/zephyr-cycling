import json

from utils import files
from lib.microdot import Microdot, send_file, Request
from data.user_config import UserConfig
from services.service_manager import ServiceLocator
from services.fan_service import FanService


app = Microdot()


@app.route('/', methods=['GET', 'POST'])
async def root(request):
    if request.method == 'GET':
        return files.read_file_as_string("../web/configuration.html"), 200, {'Content-Type': 'text/html'}
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

        # Notify the fan controller that the heart rate configuration settings have been changed.
        ServiceLocator.get(FanService).update_user_config(user_config)


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