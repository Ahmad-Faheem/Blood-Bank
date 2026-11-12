
function updateDateTime() {
    const now = new Date();
    const dayOptions = { weekday: 'long' }
    const dayString = new Intl.DateTimeFormat('en-Us', dayOptions).format(now);
    const dateOptions = { month: 'long', day: 'numeric', year: 'numeric' }
    const dateString = new Intl.DateTimeFormat('en-Us', dateOptions).format(now);

    const systemTime = document.querySelector('.system-time');
    systemTime.innerText = `[ ${dayString} ] - ${dateString}`;
}
updateDateTime();
setInterval(updateDateTime, 60000);

// sidbar menu toggle logic
const menuToggle = document.getElementById('menuToggle');
const sidebar = document.querySelector('.sidebar');
const overlay = document.getElementById('overlay');

menuToggle.addEventListener('click', () => {
    sidebar.classList.add('active');
    overlay.classList.add('active');
});

overlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
});

//  Logout modal popup logic
const logout_btn = document.querySelector('.logout-link');
const modalOverlay = document.querySelector('.modal-overlay');
const cancelBtn = document.querySelector('.btn-cancel');
const confirmBtn = document.querySelector('.btn-confirm');

function openModal() {
    modalOverlay.classList.add('active');
}
function closeModal() {
    modalOverlay.classList.remove('active');
}

logout_btn.addEventListener('click', openModal)
cancelBtn.addEventListener('click', closeModal);

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
        closeModal();
    }
});


const toastContainer = document.getElementById('toast-container');
const activeTimers = new Map();

function createToast(type, message) {
    const id = String(Date.now());
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.dataset.id = id;
    toast.innerHTML = `
            <span class="toast-msg">${message}</span>
            <button class="toast-close">&times;</button>
        `;

    if (toastContainer) {
        toastContainer.appendChild(toast);
    } else {
        document.body.appendChild(toast);
    }

    const timer = setTimeout(() => {
        removeToast(id);
    }, 4000);

    activeTimers.set(id, timer);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(id);
    });
}

function removeToast(id) {
    const stringId = String(id);
    const toast = document.querySelector(`.toast[data-id="${stringId}"]`);

    if (toast) {
        toast.classList.add('fade-out');

        if (activeTimers.has(stringId)) {
            clearTimeout(activeTimers.get(stringId));
            activeTimers.delete(stringId);
        }

        const forceRemove = setTimeout(() => {
            toast.remove();
        }, 4000);

        toast.addEventListener('animationend', () => {
            clearTimeout(forceRemove);
            toast.remove();
        });
    }
}

// Donor approve / reject request to backend 
function moderateDonor(donor_id, action) {
    const data = {
        action: action,
        donor_id: donor_id
    }
    fetch(`/api/v1/donors/${donor_id}/moderate/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`donor-row-${donor_id}`);
                if (row) row.remove();

                window.location.reload();
                if (currentCount === 0) {
                    document.getElementById('donors-table').style.display = 'none';
                    document.getElementById('empty-state').classList.remove('hidden');
                }
            }
        });
}


// Request approve / reject request to backend 
function moderateRequest(request_id, action, blood_group, units_required) {
    const data = {
        action: action,
        request_id: request_id,
        blood_group: blood_group,
        units_required: units_required
    }
    fetch(`/api/v1/requests/${request_id}/moderate/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`request-row-${request_id}`);
                if (row) row.remove();

                window.location.reload();
                if (currentCount === 0) {
                    document.getElementById('requests-table').style.display = 'none';
                    document.getElementById('empty-state').classList.remove('hidden');
                }
            }
            if (typeof createToast === 'function') {
                createToast('error', `${data.error} : ${data.message}`);
            }
        }).catch(error => {
            console.log('Error : ', error);
        })
}

// Review approve / reject request to backend 
function moderateReview(review_id, action) {
    const data = {
        action: action,
        review_id: review_id
    }
    fetch(`/api/v1/reviews/${review_id}/moderate/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const row = document.getElementById(`review-row-${review_id}`);
                if (row) row.remove();

                window.location.reload();
                if (currentCount === 0) {
                    document.getElementById('reviews-table').style.display = 'none';
                    document.getElementById('empty-state').classList.remove('hidden');
                }
            }
        });
}

