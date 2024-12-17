// Home Sayfası: Randevu Verilerini Getirme ve Gösterme
function fetchAppointments() {
    const center_name = document.getElementById('center_name').value;
    const visa_category = document.getElementById('visa_category').value;
    const appointment_date = document.getElementById('appointment_date').value;

    fetch(`/get_filtered_appointments?center_name=${center_name}&visa_category=${visa_category}&appointment_date=${appointment_date}`)
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('appointments-table-body');
            tbody.innerHTML = "";  // Mevcut verileri temizle
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.center_name}</td>
                    <td>${row.visa_category}</td>
                    <td>${row.visa_subcategory || '-'}</td>
                    <td>${row.source_country || '-'}</td>
                    <td>${row.mission_country || '-'}</td>
                    <td>${row.appointment_date || 'N/A'}</td>
                    <td>${row.last_checked || 'N/A'}</td>
                    <td>${row.people_looking || 0}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => console.error("Randevu verisi çekilirken hata: ", err));
}

// Sayfa Yüklendiğinde Veriyi Getir
document.addEventListener("DOMContentLoaded", fetchAppointments);
