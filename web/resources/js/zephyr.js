function loadUserConfig() {
    fetch("/config")
      .then(response => {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response.json()
      })
      .then(data => {

        for (let i = 1; i <= 8; i++) { 
          document.getElementById('hr' + i.toString()).value = data.relay_config[i-1][2]
          document.getElementById('en' + i.toString()).checked = (Boolean(data.relay_config[i-1][1]) == true)
        }
      })
      .catch(error => {
          console.error('Error fetching data:', error);
      });
  }