function fetchRecentAppointments() {
    fetch('/get_recent_appointments')
        .then(response => response.json())
        .then(data => {
            const recentAppointmentsDiv = document.getElementById('recent-appointments');
            if (data.length > 0) {
                recentAppointmentsDiv.innerHTML = data.map(app => `
                    <div class="log">
                        <span class="timestamp">${app.timestamp}</span>
                        <div class="log-text">${app.message}</div>
                    </div>
                `).join('');
            } else {
                recentAppointmentsDiv.innerHTML = "<div class='text-muted'>No recent appointments found.</div>";
            }
        });
  }
  
  function fetchResponses() {
    fetch('/get_responses')
        .then(response => response.json())
        .then(data => {
            const responsesDiv = document.getElementById('response-changes');
            if (data.length > 0) {
                responsesDiv.innerHTML = data.map(res => `
                    <div class="log">
                        <span class="timestamp">${res.timestamp}</span>
                        <pre class="log-text">${JSON.stringify(res.response, null, 2)}</pre>
                    </div>
                `).join('');
            } else {
                responsesDiv.innerHTML = "<div class='text-muted'>No response changes found.</div>";
            }
        });
  }
  
  function fetchLogs() {
    fetch('/get_logs')
        .then(response => response.json())
        .then(data => {
            const logsDiv = document.getElementById('all-logs');
            if (data.length > 0) {
                logsDiv.innerHTML = data.map(log => `
                    <div class="log">
                        <span class="timestamp">${log.timestamp}</span>
                        <div class="log-text">${log.message}</div>
                    </div>
                `).join('');
            } else {
                logsDiv.innerHTML = "<div class='text-muted'>No logs available.</div>";
            }
        });
  }
  

  
  // Fetch data every 10 seconds
  setInterval(() => {
    fetchRecentAppointments();
    fetchResponses();
    fetchLogs();
  }, 10000);
  
  // Initial fetch
  fetchRecentAppointments();
  fetchResponses();
  fetchLogs();
  
  