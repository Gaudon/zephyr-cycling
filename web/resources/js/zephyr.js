function loadUserConfig() {
  fetch("/config").then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json()
  }).then(data => {
    if (data != null) {
      // Relay Config
      if(data.relay_settings != null) {
        for (let i = 1; i <= 4; i++) { 
          document.getElementById('hr' + i.toString()).value = data.relay_settings[i-1][2]
          document.getElementById('en' + i.toString()).checked = (Boolean(data.relay_settings[i-1][1]) == true)
        }
      }
    }
  }).catch(error => {
      console.error('Error fetching data:', error);
  });
}

function onFanModeButtonClick(relay_id) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "relay?id=" + relay_id + "&status=1", true); 
  xhr.send();  
}

function onBleScanButtonClick() {
  if (document.getElementById('ble_status').textContent !== 'IDLE') return;
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "scan"); 
  xhr.send();

  document.getElementById('btn_ble_scan').disabled = true
  setTimeout(() => {
    document.getElementById('btn_ble_scan').disabled = false
  }, 20000);
}

function onBleDisconnectButtonClick() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "disconnect");
  xhr.send();
}

function onBleConnectButtonClick() {
  const select = document.getElementById('ble_nearby_devices');
  const address = select.options[select.selectedIndex].getAttribute('data-address') || '';
  const addressType = select.options[select.selectedIndex].getAttribute('data-type') || '';

  if (!address || !addressType) return;
  
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "connect?address=" + encodeURIComponent(address) + "&address_type=" + encodeURIComponent(addressType));
  xhr.send();
}

function onResetButtonClick() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "reset"); 
  xhr.send();  
}

function onStatusUpdate() {
  fetch("/status").then(response => {
    if (!response.ok) {
      throw new Error('Status could not be read.');
    }
    return response.json()
  }).then(data => {
    if (data != null) {
      document.getElementById('ble_status').innerText = data.ble_status.state;
      document.getElementById('ble_device_name').innerText = data.ble_status.device_name;
      document.getElementById('wlan_status').innerText = data.wlan_status.state;
      document.getElementById('wlan_network_name').innerText = data.wlan_status.network_name;

      const deviceList = data.ble_status.device_list;
      const select = document.getElementById('ble_nearby_devices');
      select.innerHTML = "";
      if (Array.isArray(deviceList) && deviceList.length > 0) {
        deviceList.forEach(d => {
          const option = document.createElement('option');
          option.textContent = d.name;
          option.setAttribute('data-address', d.address);
          option.setAttribute('data-type', d.address_type);
          select.appendChild(option);
        });
        select.selectedIndex = 0;
      }
    }
  }).catch(error => {
      console.error('Error fetching data:', error);
  });  
}

function saveUserConfig() {
  document.getElementById('settings_save_button').disabled = true

  const user_config = { 
    wifi_settings: { 
      ssid: "", 
      password: "" 
    }, 
    relay_settings: [ 
      {"en":false,"hr":"0"},
      {"en":false,"hr":"0"},
      {"en":false,"hr":"0"},
      {"en":false,"hr":"0"} 
    ]
  };

  var xhr = new XMLHttpRequest();
  
  xhr.open("POST", "/", true); 
  xhr.setRequestHeader("Content-Type", "application/json");
  
  xhr.onload = function(event) { 
    M.toast({html: 'User settings have been updated.'})
    document.getElementById('settings_save_button').disabled = false
  }; 

  xhr.onerror = function(event) {
    M.toast({html: 'An error has occurred.'})
    document.getElementById('settings_save_button').disabled = false
  };

  for (let i = 1; i <= 4; i++) {
    var relay_setting = {}
    relay_setting.en = document.getElementById('en' + i).checked
    relay_setting.hr = document.getElementById('hr' + i).value
    user_config.relay_settings[i - 1] = relay_setting
  } 

  xhr.send(JSON.stringify(user_config));
}