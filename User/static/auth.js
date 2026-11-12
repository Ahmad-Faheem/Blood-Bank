
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
    const submitButton = document.querySelector("button[type='submit']");
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
        if (form_type === 'register' || form_type === 'forget-password'
            || form_type === 'change-password' || form_type === 'login') {
            field_Id = "u_" + fieldKey;
        } else { field_Id = fieldKey; }
        const errorMessage = errors[fieldKey];
        showError(field_Id, Array.isArray(errorMessage) ? errorMessage[0] : errorMessage);
    });
}

function SendData(ev) {
    // User registration backend request logic : 
    if (ev.target.id === "u_register") {
        ev.preventDefault();
        const full_name = document.getElementById("u_full_name").value;
        const email = document.getElementById("u_email").value;
        const password = document.getElementById("u_password").value;

        const data = {
            full_name: full_name,
            email: email,
            password: password,
        }

        setSubmittingState(true);
        fetch('/api/v1/register/', {
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                window.location.href = '/User/login/';
                console.log("Account created successfully!");
            } else {
                handleBackendErrors('register', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }

    // User Login backend request logic :
    else if (ev.target.id === "u_login") {
        ev.preventDefault();
        const urlParams = new URLSearchParams(window.location.search);
        const nextParam = urlParams.get('next') || '/';
        const email = document.getElementById("u_email").value;
        const password = document.getElementById("u_password").value;
        const data = {
            email: email,
            password: password,
        }
        console.log(urlParams.get('next'));
        setSubmittingState(true);
        fetch(`/api/v1/login/?next=${encodeURIComponent(nextParam)}`, {
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                console.log("User successfully LoggedIn !");
                sessionStorage.setItem('isUserLoggedIn', true);
                if(data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
            } else {
                handleBackendErrors('login', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }

    // User Forget Password backend request logic :
    else if (ev.target.id === "u_forget_pass") {
        ev.preventDefault();
        const email = document.getElementById("u_email").value;
        const data = { email: email }

        setSubmittingState(true);
        fetch('/api/v1/forget-password/', {
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                window.location.href = '/User/verify-otp/';
                console.log("Verfiy otp recieved on ", email);
                sessionStorage.setItem('verificationEmail', email);
            } else {
                handleBackendErrors('forget-password', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }

    // User otp-verification backend request logic :
    if (ev.target.id === "otp-verification") {
        ev.preventDefault();
        const otp = document.getElementById("otp").value;
        const email = sessionStorage.getItem('verificationEmail');
        const data = {
            email: email,
            otp: otp
        }

        setSubmittingState(true);
        fetch('/api/v1/verify-otp/', {
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                console.log("otp is verified...");
                window.location.href = '/User/change-password/';
                sessionStorage.setItem('verificationToken', data.reset_token);
            } else {
                console.log('OTP verification error');
                handleBackendErrors('verify-otp', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }

    // User Change Password backend request logic :
    if (ev.target.id === "u_change_pass") {
        ev.preventDefault();
        const email = sessionStorage.getItem('verificationEmail');
        const reset_token = sessionStorage.getItem('verificationToken');
        const new_password = document.getElementById("u_new_password").value;
        const confirm_password = document.getElementById("u_confirm_password").value;
        const data = {
            email: email,
            reset_token: reset_token,
            new_password: new_password,
            confirm_password: confirm_password
        }

        setSubmittingState(true);
        fetch('/api/v1/change-password/', {
            method: "POST",
            headers: {
                "Content-type": "application/json",
                "X-CSRFToken": getCsrfToken()
            },
            body: JSON.stringify(data)
        }).then(async response => {
            const data = await response.json();
            setSubmittingState(false);
            if (response.ok) {
                console.log("otp is verified...");
                window.location.href = '/User/login/';
                sessionStorage.removeItem('verificationToken');
                sessionStorage.removeItem('verificationEmail');
            } else {
                handleBackendErrors('change-password', data);
            }
        }).catch(error => {
            setSubmittingState(false);
            console.log("API Connections error : ", error);
        });
    }
}

let New_Password = "";
const Validate = (activeId) => {
    let isValid = true;

    if (activeId === 'u_full_name') {
        const fullName = document.getElementById('u_full_name').value.trim();
        if (fullName === "") {
            isValid = false;
            showError('u_full_name', "Name is Required");
        } else if (fullName.length < 3 || !/^[a-zA-Z\s]+$/.test(fullName)) {
            isValid = false;
            showError('u_full_name', "Enter a Valid Name");
        } else {
            clearError('u_full_name');
        }
    }

    if (activeId === 'u_email') {
        const email = document.getElementById('u_email').value.trim();
        if (!/^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$/.test(email)) {
            isValid = false;
            showError('u_email', "Enter a valid Email Address");
        } else {
            clearError('u_email');
        }
    }

    if (activeId === 'u_password') {
        const pass = document.getElementById('u_password').value;
        if (pass.length < 8) {
            isValid = false;
            showError('u_password', "Password must be at least 8 characters");
        } else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/.test(pass)) {
            isValid = false;
            showError('u_password', "Must contain Upper, Lower, Digits & Symbols");
        } else {
            clearError('u_password');
        }
    }

    if (activeId === 'u_new_password') {
        const newPass = document.getElementById('u_new_password').value;
        if (newPass.length < 8) {
            isValid = false;
            showError('u_new_password', "Password must be at least 8 characters");
        } else if (!(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$/.test(newPass))) {
            isValid = false;
            showError('u_new_password', "Must contain Uppecase, Lower, Digits & Symbols");
        } else {
            New_Password = newPass;
            clearError('u_new_password');
        }
    }

    if (activeId === 'u_confirm_password') {
        const confirmPass = document.getElementById('u_confirm_password').value;
        if (confirmPass !== New_Password) {
            isValid = false;
            showError('u_confirm_password', "Passwords do not match");
        } else {
            clearError('u_confirm_password');
        }
    }
    return isValid;
};

document.addEventListener('input', (event) => {
    Validate(event.target.id);
});

document.querySelector('form').addEventListener('submit', (event) => {
    if (event.target.id === 'u_register') {
        const isFullNameValid = Validate('u_full_name');
        const isEmailValid = Validate('u_email');
        const isPassValid = Validate('u_password');

        if (!isFullNameValid || !isEmailValid || !isPassValid) {
            event.preventDefault();
        } else {
            SendData(event);
        }
    }

    if (event.target.id === 'u_login') {
        const isEmailValid = Validate('u_email');
        const isPassValid = Validate('u_password');

        if (!isEmailValid || !isPassValid) {
            event.preventDefault();
        } else {
            SendData(event);
        }
    }

    if (event.target.id === 'u_forget_pass') {
        const isEmailValid = Validate('u_email');

        if (!isEmailValid) {
            event.preventDefault();
        } else {
            SendData(event);
        }
    }

    if (event.target.id === 'u_change_pass') {
        const isNewPassValid = Validate('u_new_password');
        const isConfirmPassValid = Validate('u_confirm_password');

        if (!isNewPassValid || !isConfirmPassValid) {
            event.preventDefault();
        } else {
            SendData(event);
        }
    }
});


// _____________________________________________________________________________

// Client Side OTP Validation Logic : 
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.otp-field');
    const fullOtpInput = document.getElementById('otp');
    const errorSpan = document.getElementById('otp_error');

    inputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            const value = e.target.value;
            if (!/^\d$/.test(value)) {
                e.target.value = "";
                errorSpan.textContent = "Characters are not Allowed.";
                return;
            }
            errorSpan.textContent = "";
            if (value && index < inputs.length - 1) {
                inputs[index + 1].focus();
            }
            combineOtp();
        });
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !e.target.value && index > 0) {
                inputs[index - 1].focus();
            }
        });
    });

    function combineOtp() {
        let otpValue = "";
        inputs.forEach(input => {
            otpValue += input.value;
        });
        fullOtpInput.value = otpValue;
        if (otpValue.length === 6) {
            inputs.forEach(i => i.classList.remove('input-error'));
        }
    }

    document.getElementById('otp-verification').addEventListener('submit', (e) => {
        if (fullOtpInput.value.length !== 6) {
            e.preventDefault();
            errorSpan.textContent = "Please Enter all 6 digits.";
            inputs.forEach(i => {
                if (!i.value) i.classList.add('input-error');
            });
        } else {
            SendData(event);
        }
    });
});
