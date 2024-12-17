let dataTable;

document.addEventListener("DOMContentLoaded", () => {
    fetchDatalistOptions();
    fetchAppointments();

    // Enter tuşu ile arama
    document.getElementById("filter-form").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            fetchAppointments();
        }
    });
});

function fetchDatalistOptions() {
    const filters = ["center_name", "visa_category", "visa_subcategory", "source_country", "mission_country"];

    filters.forEach(column => {
        fetch(`/get_filter_options?column=${column}`)
            .then(response => response.json())
            .then(data => {
                // Autocomplete için hazırla
                $("#" + column).autocomplete({
                    source: data,
                    minLength: 0, // Tıklayınca tüm liste gelir
                    autoFocus: true
                }).focus(function () {
                    $(this).autocomplete("search", ""); // Focus ile açılır
                });
            })
            .catch(err => console.error(`Error fetching options for ${column}:`, err));
    });
}

function fetchAppointments() {
    const params = new URLSearchParams({
        center_name: document.getElementById("center_name").value,
        visa_category: document.getElementById("visa_category").value,
        visa_subcategory: document.getElementById("visa_subcategory").value,
        source_country: document.getElementById("source_country").value,
        mission_country: document.getElementById("mission_country").value
    });

    fetch(`/get_filtered_appointments?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (dataTable) {
                dataTable.clear().rows.add(data).draw();
            } else {
                dataTable = $("#appointments-table").DataTable({
                    data: data,
                    columns: [
                        { data: "center_name" },
                        { data: "visa_category" },
                        { data: "visa_subcategory", defaultContent: "-" },
                        { data: "source_country", defaultContent: "-" },
                        { data: "mission_country", defaultContent: "-" },
                        { data: "appointment_date", defaultContent: "N/A" },
                        { data: "last_checked", defaultContent: "N/A" },
                        { data: "people_looking", defaultContent: 0 }
                    ],
                    responsive: true,
                    pageLength: 10,
                    order: [[6, "desc"]]
                });
            }
        })
        .catch(err => console.error("Error fetching appointments:", err));
}

function clearFilters() {
    document.getElementById("filter-form").reset();
    fetchAppointments();
}
