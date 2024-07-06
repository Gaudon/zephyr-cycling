function setup() {
  document.getElementById('settings_save_button').disabled = true

  var user_config = {}

  user_config.wifi_settings = {}
  user_config.wifi_settings.ssid = document.getElementById('wifi_ssid').value
  user_config.wifi_settings.password = document.getElementById('wifi_password').value

  user_config.relay_settings = []
  for (let i = 1; i <= 4; i++) {
    var relay_setting = {}
    relay_setting.en = document.getElementById('en' + i).checked
    relay_setting.hr = document.getElementById('hr' + i).value
    user_config.relay_settings.push(relay_setting)
  }

  fetch("http://192.168.4.1/setup", {
    method: "POST",
    body: JSON.stringify(user_config),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  });
}