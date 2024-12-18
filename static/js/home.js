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
                        {
                            data: "appointment_date",
                            render: function (data) {
                                return formatDate(data);
                            },
                            defaultContent: "N/A"
                        },
                        {
                            data: "last_checked",
                            render: function (data) {
                                return formatDateTime(data);
                            },
                            defaultContent: "N/A"
                        },
                        { data: "people_looking", defaultContent: 0 },
                        {
                            data: "book_now_link",
                            render: function (data) {
                                return `<a href="${data}" target="_blank" class="btn btn-primary btn-sm">
                                            <i class="bi bi-box-arrow-up-right"></i>
                                        </a>`;
                            }
                        },
                        {
                            data: "unique_appointment_id",
                            render: function (data) {
                                return `<button class="btn btn-secondary btn-sm" onclick="viewLogs(${data})">
                                            <i class="bi bi-journal-text"></i>
                                        </button>`;
                            }
                        }
                    ],
                    responsive: true,
                    pageLength: 10,
                    order: [[6, "desc"]]
                });
            }
            updateFilterOptions(data);
        })
        .catch(err => console.error("Error fetching appointments:", err));
}

function clearFilters() {
    document.getElementById("filter-form").reset();
    fetchAppointments();
}


function updateFilterOptions(data) {
    const filters = {
        center_name: new Set(),
        visa_category: new Set(),
        visa_subcategory: new Set(),
        source_country: new Set(),
        mission_country: new Set()
    };

    // Gelen verilerden mevcut filtre değerlerini topla
    data.forEach(item => {
        if (item.center_name) filters.center_name.add(item.center_name);
        if (item.visa_category) filters.visa_category.add(item.visa_category);
        if (item.visa_subcategory) filters.visa_subcategory.add(item.visa_subcategory);
        if (item.source_country) filters.source_country.add(item.source_country);
        if (item.mission_country) filters.mission_country.add(item.mission_country);
    });

    // Her filtre için güncellenmiş seçenekleri uygula
    Object.keys(filters).forEach(column => {
        const options = Array.from(filters[column]).sort(); // Set'i diziye çevir ve sırala
        const autocompleteElement = $("#" + column);

        autocompleteElement.autocomplete({
            source: options,
            minLength: 0,
            autoFocus: true
        }).focus(function () {
            $(this).autocomplete("search", "");
        });
    });
}


function viewLogs(appointmentId) {
    fetch(`/logs_modal?appointment_id=${appointmentId}`)
        .then(response => response.text())
        .then(htmlContent => {
            // Yeni modal oluştur
            const modalHtml = `
                <div class="modal fade" id="dynamicLogsModal" tabindex="-1" aria-labelledby="dynamicLogsModalLabel" aria-hidden="true">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            ${htmlContent}
                        </div>
                    </div>
                </div>
            `;

            // Modal'ı DOM'a ekle
            document.body.insertAdjacentHTML("beforeend", modalHtml);
            const modal = new bootstrap.Modal(document.getElementById("dynamicLogsModal"));
            modal.show();

            // Modal kapandıktan sonra DOM'dan kaldır
            document.getElementById("dynamicLogsModal").addEventListener("hidden.bs.modal", () => {
                document.getElementById("dynamicLogsModal").remove();
            });
        })
        .catch(err => console.error("Error loading logs modal:", err));
}


// Tarih formatlama fonksiyonu (sadece tarih)
function formatDate(dateString) {
    if (!dateString) return "N/A";

    const date = new Date(dateString); // Tarih objesine çevir
    const options = { day: "2-digit", month: "2-digit", year: "numeric" };
    return new Intl.DateTimeFormat("tr-TR", options).format(date);
}


// Tarih formatlama fonksiyonu (tarih + saat)
function formatDateTime(dateString) {
    if (!dateString) return "N/A";

    const date = new Date(dateString); // Tarih objesine çevir
    const options = { 
        day: "2-digit", 
        month: "2-digit", 
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    };
    return new Intl.DateTimeFormat("tr-TR", options).format(date);
}
