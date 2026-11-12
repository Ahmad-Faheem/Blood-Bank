
function openTab(event, tabName) {
    const tabContent = document.getElementsByClassName("tab-content");
    for (let i = 0; i < tabContent.length; i++) {
        tabContent[i].classList.remove("active");
    }

    const tabBtns = document.getElementsByClassName("tab-btn");
    for (let i = 0; i < tabBtns.length; i++) {
        tabBtns[i].classList.remove("active-btn");
    }

    document.getElementById(tabName).classList.add("active");
    if (tabName === "donor") {
        tabBtns[0].classList.add("active-btn");
        localStorage.setItem('profile-tab', 'Donor');
    } else if (tabName === "requester") {
        tabBtns[1].classList.add("active-btn");
        localStorage.setItem('profile-tab', 'Requester');
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const profile_tab = localStorage.getItem('profile-tab');
    if (profile_tab === "Donor") {
        openTab(event, 'donor');
    } else if (profile_tab === 'Requester') {
        openTab(event, 'requester');
    }
});

function openHistoryTab(event, tabName) {
    const history_content = document.getElementsByClassName("history-content");
    for (let i = 0; i < history_content.length; i++) {
        history_content[i].classList.remove("active");
    }

    const history_tab = document.getElementsByClassName("history-tab");
    for (let i = 0; i < history_tab.length; i++) {
        history_tab[i].classList.remove("active-btn");
    }

    document.getElementById(tabName).classList.add("active");
    if (tabName === "donor-history-tab") {
        history_tab[0].classList.add("active-btn");
        localStorage.setItem('eligibility-tab', 'donor-history');
    } else if (tabName === "request-history-tab") {
        history_tab[1].classList.add("active-btn");
        localStorage.setItem('eligibility-tab', 'request-history');
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const eligibility_tab = localStorage.getItem('eligibility-tab');
    if (eligibility_tab === "donor-history") {
        openHistoryTab(event, 'donor-history-tab');
    } else if (eligibility_tab === 'request-history') {
        openHistoryTab(event, 'request-history-tab');
    }
});

const showError = (elementId, message) => {
    const el = document.getElementById(elementId);
    const msgTag = el.parentElement.querySelector('.error-text');
    if (msgTag) msgTag.innerText = message;
    el.style.borderColor = "var(--error)";
};

const clearError = (inputId) => {
    const input = document.getElementById(inputId);
    const container = input.closest('.input-container');
    const errorSpan = container.querySelector('.error-text');
    input.style.borderColor = "var(--border)";
    errorSpan.textContent = "";
};

let submitButtonText;
function setSubmittingState(isSubmitting) {
    const submitButton = document.querySelector("#profile-save-btn");
    if (isSubmitting) {
        submitButtonText = submitButton.innerText;
        submitButton.disabled = true;
        submitButton.innerText = "Processing...";
        submitButton.style.opacity = "0.7";
    } else {
        submitButton.disabled = false;
        submitButton.innerText = submitButtonText;
        submitButton.style.opacity = "1";
    }
}

function getCsrfToken() {
    const tokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    return tokenInput ? tokenInput.value : "";
}

function handleBackendErrors(form_type, errors) {
    Object.keys(errors).forEach((fieldKey) => {
        if (form_type === 'register') {
            field_Id = "u_" + fieldKey;
        } else { field_Id = fieldKey; }
        const errorMessage = errors[fieldKey];
        showError(field_Id, Array.isArray(errorMessage) ? errorMessage[0] : errorMessage);
    });
}

/* Back to Top button toggle logic */
const backToTopBtn = document.getElementById("backToTop");
let isScrolling;

window.onscroll = function () {
    if (document.body.scrollTop > 300 || document.documentElement.scrollTop > 300) {
        backToTopBtn.classList.add("show");
    } else {
        backToTopBtn.classList.remove("show");
    }
    window.clearTimeout(isScrolling);

    isScrolling = setTimeout(function () {
        if (document.documentElement.scrollTop > 300) {
            backToTopBtn.classList.remove("show");
        }
    }, 2000);
};

backToTopBtn.addEventListener("click", () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
});

/* Navbar Toggle logic */
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const navLinks = document.getElementById('navLinks');
    const modalOverlay = document.querySelector('.modal-overlay');

    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
        modalOverlay.classList.toggle('active');
        if (navLinks.classList.contains('active')) {
            menuToggle.innerHTML = '✕';
        } else {
            menuToggle.innerHTML = '☰';
        }
    });

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) {
            navLinks.classList.toggle('active');
            modalOverlay.classList.toggle('active');
            if (navLinks.classList.contains('active')) {
                menuToggle.innerHTML = '✕';
            } else {
                menuToggle.innerHTML = '☰';
            }
        }
    });

});

// Show the success and Error Notifications Stack
const toastContainer = document.getElementById('toast-container');
const activeTimers = new Map();

function createToast(type, message) {
    const id = Date.now();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.dataset.id = id;
    toast.innerHTML = `
            <span class="toast-msg">${message}</span>
            <button class="toast-close">&times;</button>
        `;
    toastContainer.appendChild(toast);
    const timer = setTimeout(() => {
        removeToast(id);
    }, 4000);
    activeTimers.set(id, timer);
    toast.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(id);
    });
}

function removeToast(id) {
    const toast = document.querySelector(`.toast[data-id="${id}"]`);
    if (toast) {
        toast.classList.add('fade-out');
        if (activeTimers.has(id)) {
            clearTimeout(activeTimers.get(id));
            activeTimers.delete(id);
        }
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }

    if (sessionStorage.getItem('isUserLoggedIn') === 'true') {
        sessionStorage.removeItem('isUserLoggedIn');
    }
    else if (sessionStorage.getItem('isDonorRegistered') === 'true') {
        sessionStorage.removeItem('isDonorRegistered');
    }
    else if (sessionStorage.getItem('isBloodRequested') === 'true') {
        sessionStorage.removeItem('isBloodRequested');
    }
    else if (sessionStorage.getItem('isProfileUpdated') === 'true') {
        sessionStorage.removeItem('isProfileUpdated');
    }
}

if (sessionStorage.getItem('isUserLoggedIn') === 'true') {
    createToast('success', 'User LoggedIn Successfully !');
}
if (sessionStorage.getItem('isDonorRegistered') === 'true') {
    createToast('success', 'Donor Registered, Wait for Screening !');
}
if (sessionStorage.getItem('isBloodRequested') === 'true') {
    createToast('success', 'Blood Requested, Wait for Approval !');
}
if (sessionStorage.getItem('isProfileUpdated') === 'true') {
    createToast('success', 'Profile Updated Successfully !');
}


/* All Reviews page client side filter logic */
function filterReviews(targetRole, event) {
    const buttons = document.querySelectorAll('.filter-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    event.currentTarget.classList.add('active');
    const cards = document.querySelectorAll('.approved-review-card');

    cards.forEach(card => {
        const cardRole = card.getAttribute('data-role');

        if (targetRole === 'all' || cardRole === targetRole) {
            card.style.display = 'flex';
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50);
        } else {
            card.style.opacity = '0';
            card.style.transform = 'translateY(10px)';
            card.style.display = 'none';
        }
    });
}


function updateProfile(ev) {
    if (ev.target.id === "profile-edit-form") {
        ev.preventDefault();
        setSubmittingState(true);
        const formData = new FormData();

        formData.append('full_name', document.getElementById("full_name").value);
        formData.append('address', document.getElementById("address").value);
        formData.append('status', document.getElementById("status").value);
        formData.append('country_code', document.getElementById("country_code").value);
        formData.append('phone', document.getElementById("phone").value);
        formData.append('description', document.getElementById("description").value);

        const imageInput = document.getElementById("p_image");
        if (imageInput.files.length > 0) {
            formData.append('profile_image', imageInput.files[0]);
        }

        fetch('/api/v1/profile/update/', {
            method: "PUT",
            headers: {
                "X-CSRFToken": getCsrfToken()
            },
            body: formData
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                console.log("Profile updated successfully!");
                sessionStorage.setItem('isProfileUpdated', true);
                window.location.reload();
            } else {
                handleBackendErrors('profile-edit', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }
}

/* Reviews Submission Form logic */

function submitReview(event) {
    event.preventDefault();

    const nameInput = document.getElementById('reviwer_name');
    const emailInput = document.getElementById('reviwer_email');
    const roleInput = document.getElementById('reviwer_role');
    const commentInput = document.getElementById('reviwer_comment');
    const checkedRating = document.querySelector('input[name="user-rating"]:checked');

    if (!nameInput.value || !roleInput.value || !commentInput.value || !checkedRating) {
        if (typeof createToast === 'function') {
            createToast('error', 'Please fill out all fields and select a star rating.');
        } else {
            alert('Please complete all form fields.');
        }
        return;
    }
    const authorName = nameInput.value.trim();

    const formData = {
        reviwer_name: nameInput.value,
        reviwer_email: emailInput.value,
        reviwer_role: roleInput.value,
        reviwer_comment: commentInput.value,
        'user_rating': parseInt(checkedRating.value)
    };

    fetch('/api/v1/reviews/submit/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(formData)
    })
        .then(res => {
            if (res.ok) {
                if (typeof createToast === 'function') {
                    createToast('success', `Thank you, ${authorName}! Your review has successfully submitted.`);
                }
                document.getElementById('public-review-form').reset();
            } else {
                console.log('error');
            }
        });
}

/* Profile Edit section logic */

document.getElementById('profile-edit-form').addEventListener('submit', (event) => {
    updateProfile(event);
});

// Edit Profile models toggle logic 
const edit_profile_section = document.querySelector('#edit-profile-section');
const edit_profile_btn = document.querySelector('.edit-profile-btn');

function openEditModal() {
    edit_profile_section.classList.add('active');
}
function closeEditModal() {
    edit_profile_section.classList.remove('active');
}
edit_profile_btn.addEventListener('click', openEditModal);

document.getElementById('edit-profile-section').addEventListener('submit', (event) => {
    event.preventDefault();
});
edit_profile_section.addEventListener('click', (e) => {
    if (e.target === edit_profile_section) {
        closeEditModal();
    }
});

// Profile Edit form image preview logic 
const imgInput = document.getElementById("p_image");
const imgPrevContainer = document.getElementById("img_preview");

// --- Image Handling ---
imgInput.addEventListener("change", function () {
    imgPrevContainer.innerHTML = "";
    const files = Array.from(this.files);
    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.className = "img-prev";
            imgPrevContainer.appendChild(img);
        };
        reader.readAsDataURL(file);
    });
});