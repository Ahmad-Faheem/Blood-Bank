
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

const STORAGE_KEY = "request_blood";

function loadFromSession() {
    const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
    if (saved) {
        Object.keys(saved).forEach(key => {
            const el = document.getElementById(key);
            if (el && el.type !== 'file') el.value = saved[key];
        });
    }
    const urgency_time_state = JSON.parse(sessionStorage.getItem("urgency_time_state"));
    if (urgency_time_state) {
        const urgency_time_input = document.getElementById('urgency_time_input');
        urgency_time_input.classList.add('active');
    }
}

function saveToSession() {
    const data = {};
    document.querySelectorAll(".input-container input, .input-container textarea, .input-container select, #country_code_input_box input").forEach(el => {
        if (el.id && el.type !== 'file') data[el.id] = el.value;
    });
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    sessionStorage.setItem("urgency_time_state", JSON.stringify(urgency_time_state));
}

function updateWizard() {
    steps.forEach((step, index) => {
        step.classList.toggle("active", index === currentStep);
        circles[index].classList.toggle("active", index === currentStep);
        circles[index].classList.toggle("completed", index < currentStep);
    });

    backBtn.classList.toggle("hidden", currentStep === 0);
    nextBtn.innerText = currentStep === steps.length - 1 ? "Request" : "Next";
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
            sendDatatoBackend()
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

let urgency_time_state = false;
const urgency_level = document.getElementById('urgency_level');
const urgency_time = document.getElementById('urgency_time');
const urgency_time_input = document.getElementById('urgency_time_input');
urgency_level.addEventListener("input", (event) => {
    if (event.target.value === 'plan') {
        urgency_time_input.classList.add('active');
        urgency_time_state = true;
    } else {
        urgency_time_input.classList.remove('active');
        urgency_time_state = false;
        urgency_time.value = "";
    }
});

const stepValidation = (stepIndex) => {
    let isValid = true;

    if (stepIndex === 0) {          // Basic Info
        const email = document.getElementById('email').value.trim();
        if (!/^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$/.test(email)) {
            isValid = false;
            showError('email', "Enter a Valid Email Address");
        } else {
            document.getElementById('email').style.borderColor = "var(--border)";
        }
        const patient_name = document.getElementById('patient_name').value.trim();
        if (patient_name.length < 3) {
            isValid = false;
            showError('patient_name', "Enter a Valid Name");
        } else {
            document.getElementById('patient_name').style.borderColor = "var(--border)";
        }
        const units_required = document.getElementById('units_required').value;
        if (units_required < 1 || units_required > 10) {
            isValid = false;
            showError('units_required', "Enter units between 1 - 10");
        } else {
            document.getElementById('units_required').style.borderColor = "var(--border)";
        }
        if (urgency_time_state) {
            const urgency_time = document.getElementById('urgency_time').value;
            if (urgency_time < 1 || urgency_time > 10) {
                isValid = false;
                showError('urgency_time', "Urgency Time must be 1 - 10 Days");
            } else {
                document.getElementById('urgency_time').style.borderColor = "var(--border)";
            }
        }
    }

    if (currentStep === 1) {
        const hospital_name = document.getElementById('hospital_name').value.trim();
        if (hospital_name.length < 5) {
            isValid = false;
            showError('hospital_name', "Enter a Valid Hospital Name");
        } else {
            document.getElementById('hospital_name').style.borderColor = "var(--border)";
        }
        const hospital_address = document.getElementById('hospital_address').value.trim();
        if (!/^[a-zA-Z0-9\s,.-]+$/.test(hospital_address)) {
            isValid = false;
            showError('hospital_address', "Invalid Address : Contains Forbidden Special Characters");
        } else {
            document.getElementById('hospital_address').style.borderColor = "var(--border)";
        }
        const doctor_name = document.getElementById('doctor_name').value.trim();
        if (doctor_name.length < 3) {
            isValid = false;
            showError('doctor_name', "Enter a Valid Doctor Name.");
        } else {
            document.getElementById('doctor_name').style.borderColor = "var(--border)";
        }
        const doctor_phone = document.getElementById('doctor_phone').value.trim();
        if (!/^\d{10,15}$/.test(doctor_phone)) {
            isValid = false;
            showError('doctor_phone', "Only 10 - 15 digits are Allowed ");
            document.getElementById('country_code').style.borderColor = "var(--error)";
        } else {
            document.getElementById('doctor_country_code').style.borderColor = "var(--border)";
            document.getElementById('doctor_phone').style.borderColor = "var(--border)";
        }
    }

    if (currentStep === 2) {
        const requester_name = document.getElementById('requester_name').value.trim();
        if (requester_name.length < 3) {
            isValid = false;
            showError('requester_name', "Enter a Valid Requester Name.");
        } else {
            document.getElementById('requester_name').style.borderColor = "var(--border)";
        }
        const requester_phone = document.getElementById('requester_phone').value.trim();
        if (!/^\d{10,15}$/.test(requester_phone)) {
            isValid = false;
            showError('requester_phone', "Only 10 - 15 digits are Allowed ");
            document.getElementById('country_code').style.borderColor = "var(--error)";
        } else {
            document.getElementById('requester_country_code').style.borderColor = "var(--border)";
            document.getElementById('requester_phone').style.borderColor = "var(--border)";
        }
    }
    return isValid;
}



function sendDatatoBackend() {
    const email = document.getElementById("email").value;
    const patient_name = document.getElementById("patient_name").value;
    const blood_group = document.getElementById("blood_group").value;
    const blood_type = document.getElementById("blood_type").value;
    const units_required = document.getElementById("units_required").value;
    const urgency_level = document.getElementById("urgency_level").value;
    const urgency_time = document.getElementById("urgency_time").value;

    const hospital_name = document.getElementById("hospital_name").value;
    const hospital_address = document.getElementById("hospital_address").value;
    const doctor_name = document.getElementById("doctor_name").value;
    const doctor_country_code = document.getElementsByName("doctor_country_code").value;
    const doctor_phone = document.getElementById("doctor_phone").value;

    const requester_name = document.getElementById("requester_name").value;
    const requester_country_code = document.getElementsByName("requester_country_code").value;
    const requester_phone = document.getElementById("requester_phone").value;
    const relationship = document.getElementById("relationship").value;

    const fileInput = document.getElementById('prescription_doc');
    const file = fileInput.files[0];
    const additional_notes = document.getElementById("additional_notes").value;

    const formData = new FormData();
    formData.append("email", email);
    formData.append("patient_name", patient_name);
    formData.append("blood_group", blood_group);
    formData.append("blood_type", blood_type);
    formData.append("units_required", units_required);
    formData.append("urgency_level", urgency_level);

    if (urgency_level !== 'plan') {
        formData.append("urgency_time", "");
    } else {
        formData.append("urgency_time", urgency_time);
    }

    formData.append("hospital_name", hospital_name);
    formData.append("hospital_address", hospital_address);
    formData.append("doctor_name", doctor_name);
    formData.append("doctor_country_code", doctor_country_code);
    formData.append("doctor_phone", doctor_phone);

    formData.append("requester_name", requester_name);
    formData.append("requester_country_code", requester_country_code);
    formData.append("requester_phone", requester_phone);
    formData.append("relationship", relationship);

    formData.append("additional_notes", additional_notes);
    if (file) {
        formData.append("prescription_doc", file);
    }
    setSubmittingState(true);
    fetch('/api/v1/blood-request/', {
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
                sessionStorage.removeItem("urgency_time_state");
                console.log(patient_name, "Blood Requested Successfully");
                sessionStorage.setItem('isBloodRequested', true);
            } else {
                handleBackendErrors(data);
            }
        })
        .catch(error => {
            if (typeof setSubmittingState === "function") setSubmittingState(false);
            console.error("API Connection error: ", error);
        });
}
