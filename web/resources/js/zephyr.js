function loadUserConfig() {
  fetch("/config").then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json()
  }).then(data => {
    if (data != null && data.relay_config != null) {
      for (let i = 1; i <= 8; i++) { 
        document.getElementById('hr' + i.toString()).value = data.relay_config[i-1][2]
        document.getElementById('en' + i.toString()).checked = (Boolean(data.relay_config[i-1][1]) == true)
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
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "scan"); 
  xhr.send();  
}

function onResetButtonClick() {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "reset"); 
  xhr.send();  
}

function saveUserConfig() {
  document.getElementById('settings_save_button').disabled = true

  var user_config = []
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
    user_config.push(relay_setting)
  } 

  xhr.send(JSON.stringify(user_config));
}