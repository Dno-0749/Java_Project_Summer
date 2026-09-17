document.addEventListener("DOMContentLoaded", function () {
    // Sidebar toggle
    const toggleBtn = document.getElementById("menu-toggle");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function (e) {
            e.preventDefault();
            document.getElementById("wrapper").classList.toggle("toggled");
        });
    }

    // Auto-dismiss alerts after 4s
    document.querySelectorAll(".alert-dismissible").forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });
    const activitySearch = document.getElementById("activitySearch");

    if (activitySearch) {
        activitySearch.addEventListener("input", function () {
            const keyword = this.value.toLowerCase().trim();
            const rows = document.querySelectorAll("#activitiesTable tbody tr");

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(keyword) ? "" : "none";
            });
        });
    }

    const excursionSearch = document.getElementById("excursionSearch");

    if (excursionSearch) {
        excursionSearch.addEventListener("input", function () {
            const keyword = this.value.toLowerCase().trim();
            const rows = document.querySelectorAll("#excursionsTable tbody tr");

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(keyword) ? "" : "none";
            });
        });
    }

    const registrationSearch = document.getElementById("registrationSearch");

    if (registrationSearch) {
        registrationSearch.addEventListener("input", function () {
            const keyword = this.value.toLowerCase().trim();
            const rows = document.querySelectorAll("#registrationsTable tbody tr");

            rows.forEach(function (row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(keyword) ? "" : "none";
            });
        });
    }

    document.querySelectorAll(".checkin-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            this.innerHTML = '<i class="bi bi-check-lg me-1"></i> Đã check-in';
            this.classList.remove("btn-success");
            this.classList.add("btn-outline-secondary");
            this.disabled = true;

            const row = this.closest("tr");

            if (row) {
                const badge = row.querySelector(".badge");

                if (badge) {
                    badge.className = "badge bg-success";
                    badge.innerHTML = '<i class="bi bi-check-lg me-1"></i> Đã check-in';
                }
            }
        });
    });
});
