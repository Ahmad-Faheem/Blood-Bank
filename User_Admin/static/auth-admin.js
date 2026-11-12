const showError = (elementId, message) => {
    const el = document.getElementById(elementId);
    if (!el) return;
    const msgTag = el.parentElement.querySelector('.error-text');
    if (msgTag) msgTag.innerText = message;
    el.style.borderColor = "var(--error)";
};

const clearError = (inputId) => {
    const input = document.getElementById(inputId);
    if (!input) return;
    const container = input.closest('.input-container');
    const errorSpan = container.querySelector('.error-text');
    input.style.borderColor = "var(--border)";
    errorSpan.textContent = "";
};

let submitButtonText;
function setSubmittingState(isSubmitting) {
    const submitButton = document.querySelector("button[type='submit']");
    if (!submitButton) return;
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
        let field_Id = "";
        if (form_type === 'admin-login'){
            field_Id = "admin_" + (fieldKey === 'username' || fieldKey === 'email' ? 'email' : 'pass');
        }
        const errorMessage = errors[fieldKey];
        showError(field_Id, Array.isArray(errorMessage) ? errorMessage[0] : errorMessage);
    });
}

function SendData(ev) {
    if (ev.target.id === "admin-login") {
        ev.preventDefault();
        const email = document.getElementById("admin_email").value;
        const password = document.getElementById("admin_pass").value;
        const data = {
            email: email,
            password: password,
        };

        setSubmittingState(true);
        fetch('/api/v1/admin-login/', { 
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const resData = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                console.log("Admin successfully LoggedIn!");
                console.log(resData.redirect_url)
                if(resData.redirect_url) {
                    window.location.href = resData.redirect_url;
                }
            } else {
                handleBackendErrors('admin-login', resData);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }
}

const Validate = (activeId) => {
    let isValid = true;

    if (activeId === 'admin_email') {
        const email = document.getElementById('admin_email').value.trim();
        if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email)) {
            isValid = false;
            showError('admin_email', "Enter a valid Email Address");
        } else {
            clearError('admin_email');
        }
    }

    // FIXED: Pointed to 'admin_pass' instead of non-existent password id element
    if (activeId === 'admin_pass') {
        const pass = document.getElementById('admin_pass').value;
        if (pass.length < 8) {
            isValid = false;
            showError('admin_pass', "Password must be at least 8 characters");
        } else {
            clearError('admin_pass');
        }
    }
    return isValid;
};

document.addEventListener('input', (event) => {
    Validate(event.target.id);
});

document.querySelector('form').addEventListener('submit', (event) => {
    if (event.target.id === 'admin-login') {
        const isEmailValid = Validate('admin_email');
        const isPassValid = Validate('admin_pass');

        if (!isEmailValid || !isPassValid) {
            event.preventDefault();
        } else {
            SendData(event);
        }
    }
});