
let submitButtonText;
function setSubmittingState(isSubmitting) {
    const submitButton = document.getElementById('nextBtn');
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

function handleBackendErrors(errors) {
    const errorListContainer = document.getElementById('backend-global-errors');
    const errorList = document.getElementById('backend-error-list');
    
    errorList.innerHTML = "";
    errorListContainer.classList.add('hidden');

    if (typeof errors === 'string') {
        const li = document.createElement('li');
        li.innerText = errors;
        errorList.appendChild(li);
        errorListContainer.classList.remove('hidden');
        return;
    }

    Object.keys(errors).forEach((fieldKey) => {
        const messages = Array.isArray(errors[fieldKey]) ? errors[fieldKey] : [errors[fieldKey]];
        
        messages.forEach(message => {
            const li = document.createElement('li');
            const cleanKey = fieldKey.replace(/_/g, ' ');
            li.innerHTML = `<strong>${cleanKey !== 'non field errors' ? cleanKey + ': ' : ''}</strong>${message}`;
            errorList.appendChild(li);

            const inputEl = document.getElementById(fieldKey);
            if (inputEl) {
                inputEl.style.borderColor = "var(--error)";
                const msgTag = inputEl.parentElement.querySelector('.error-text');
                if (msgTag) {
                    msgTag.innerText = message;
                }
            }
        });
    });

    errorListContainer.classList.remove('hidden');
    errorListContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

const steps = document.querySelectorAll(".form-step");
const circles = document.querySelectorAll(".step-circle");
const nextBtn = document.getElementById("nextBtn");
const backBtn = document.getElementById("backBtn");
let currentStep = 0;

const STORAGE_KEY = "register_donor";

function loadFromSession() {
    const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
    if (saved) {
        Object.keys(saved).forEach(key => {
            const el = document.getElementById(key);
            if (el && el.type !== 'file') el.value = saved[key];
        });
    }
}

function saveToSession() {
    const data = {};
    document.querySelectorAll("#agency-wizard input, #agency-wizard textarea, #agency-wizard select").forEach(el => {
        if (el.id && el.type !== 'file') data[el.id] = el.value;
    });
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function updateWizard() {
    steps.forEach((step, index) => {
        step.classList.toggle("active", index === currentStep);
        circles[index].classList.toggle("active", index === currentStep);
        circles[index].classList.toggle("completed", index < currentStep);
    });

    backBtn.classList.toggle("hidden", currentStep === 0);
    nextBtn.innerText = currentStep === steps.length - 1 ? "Register" : "Next";
}

function validateStep() {
    const activeStep = steps[currentStep];
    const inputs = activeStep.querySelectorAll("input[required], textarea[required], select[required]");
    let valid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.style.borderColor = "#d9534f";
            valid = false;
        } else {
            input.style.borderColor = "#ced4da";
        }
    });
    return valid;
}

nextBtn.addEventListener("click", () => {
    document.querySelectorAll(".error-text").forEach(p => p.innerText = "");
    document.querySelectorAll(".input-container input, .input-container textarea, .input-container select").forEach(el => {
        el.style.borderColor = "var(--border)";
    });

    const globalErrors = document.getElementById('backend-global-errors');
    if (globalErrors) {
        globalErrors.classList.add('hidden');
        document.getElementById('backend-error-list').innerHTML = "";
    }

    if (!validateStep()) { return; }
    const isValid = stepValidation(currentStep);
    if (isValid) {
        if (currentStep < steps.length - 1) {
            currentStep++;
            updateWizard();
            saveToSession();
            sessionStorage.setItem("Active_Step", currentStep);
        } else {
            sendDatatoBackend();
        }
    }
});

backBtn.addEventListener("click", () => {
    if (currentStep > 0) {
        currentStep--;
        updateWizard();
        sessionStorage.setItem("Active_Step", currentStep);
    }
});

document.addEventListener("DOMContentLoaded", () => {
    let savedStep = sessionStorage.getItem("Active_Step");
    if (savedStep !== null) {
        currentStep = parseInt(savedStep, 10);
        updateWizard();
    } else {
        currentStep = 0;
        updateWizard();
    }
});

document.addEventListener("input", saveToSession);
window.onload = loadFromSession;

const showError = (elementId, message) => {
    const el = document.getElementById(elementId);
    const msgTag = el.parentElement.querySelector('.error-text');
    if (msgTag) msgTag.innerText = message;
    el.style.borderColor = "var(--error)";
};

function validateDonorAge(birthDateString) {
    const today = new Date();
    const birthDate = new Date(birthDateString);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    if (age >= 18 && age <= 55) {
        return { valid: true, age: age };
    } else {
        return {
            valid: false,
            message: age < 18 ? "Donor must be at least 18 years old" : "Donor must be 55 years or under it",
        };
    }
}

let errorMsg = "";
const stepValidation = (stepIndex) => {
    let isValid = true;

    if (stepIndex === 0) {          // Basic Info
        const donor_name = document.getElementById('donor_name').value.trim();
        if (donor_name.length < 3 || donor_name.length > 80) {
            isValid = false;
            errorMsg = "Donor Name should be 3 - 80 characters";
            showError('donor_name', errorMsg);
        } else {
            document.getElementById('donor_name').style.borderColor = "var(--border)";
        }
        const date_of_birth = document.getElementById('date_of_birth').value.trim();
        const result = validateDonorAge(date_of_birth);
        if (!result.valid) {
            isValid = result.valid;
            showError('date_of_birth', result.message);
        } else {
            document.getElementById('date_of_birth').style.borderColor = "var(--border)";
        }
    }

    if (currentStep === 1) {
        const email = document.getElementById('email').value.trim();
        if (!/^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$/.test(email)) {
            isValid = false;
            showError('email', "Enter a Valid Email Address");
        } else {
            document.getElementById('email').style.borderColor = "var(--border)";
        }
        const phone = document.getElementById('phone').value.trim();
        if (!/^\d{10,15}$/.test(phone)) {
            isValid = false;
            errorMsg = "Only 10 - 15 digits are Allowed ";
            showError('phone', errorMsg);
            document.getElementById('country_code').style.borderColor = "var(--error)";
        } else {
            document.getElementById('country_code').style.borderColor = "var(--border)";
            document.getElementById('phone').style.borderColor = "var(--border)";
        }
        const address = document.getElementById('address').value.trim();
        if (!/^[a-zA-Z0-9\s,.-]+$/.test(address)) {
            isValid = false;
            errorMsg = "Invalid Address : Contains Forbidden Special Characters";
            showError('address', errorMsg);
        } else {
            document.getElementById('address').style.borderColor = "var(--border)";
        }
    }

    if (currentStep === 2) {
        const weight = document.getElementById('weight').value.trim();
        if (!/^(5\d|[6-9]\d|1\d{2})(\.\d{1,2})?$/.test(weight)) {
            isValid = false;
            errorMsg = "Weight must be between 50 - 200 kg";
            showError('weight', errorMsg);
        } else {
            document.getElementById('weight').style.borderColor = "var(--border)";
        }
    }
    return isValid;
}


function sendDatatoBackend() {
    const donor_name = document.getElementById("donor_name").value;
    const date_of_birth = document.getElementById("date_of_birth").value;
    const email = document.getElementById("email").value;
    const country_code = document.getElementById("country_code").value;
    const phone = document.getElementById("phone").value;
    const address = document.getElementById("address").value;
    const gender = document.getElementById("gender").value;
    const blood_group = document.getElementById("blood_group").value;
    const medical_notes = document.getElementById("medical_notes").value;
    const selectedRadio = document.querySelector('input[name="donation_type"]:checked');
    const donation_type = selectedRadio ? selectedRadio.value : 'whole';
    const weightRaw = document.getElementById("weight").value;
    const weight = parseFloat(weightRaw).toFixed(2);
    const fileInput = document.getElementById('donor_report');
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("donor_name", donor_name);
    formData.append("date_of_birth", date_of_birth);
    formData.append("email", email);
    formData.append("country_code", country_code);
    formData.append("phone", phone);
    formData.append("address", address);
    formData.append("gender", gender);
    formData.append("blood_group", blood_group);
    formData.append("weight", weight);
    formData.append("donation_type", donation_type);
    formData.append("medical_notes", medical_notes);

    if (file) {
        formData.append("donor_report", file);
    }
    setSubmittingState(true);
    fetch('/api/v1/register-donor/', {
        method: 'POST',
        body: formData,
        headers: {
            "X-CSRFToken": getCsrfToken()
        }, credentials: 'same-origin'
    })
        .then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                window.location.href = "/profile/";
                sessionStorage.removeItem(STORAGE_KEY);
                sessionStorage.removeItem("Active_Step");
                console.log(donor_name, "Donor Registered Successfully");
                sessionStorage.setItem('isDonorRegistered', true);
            } else {
                handleBackendErrors(data);
            }
        })
        .catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
}

