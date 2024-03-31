function setup() {
  document.getElementById('settings_save_button').disabled = true

  var user_config = {}
  var xhr = new XMLHttpRequest();

  xhr.open("POST", "/", true);
  xhr.setRequestHeader("Content-Type", "application/json");

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
  xhr.send(JSON.stringify(user_config));
}