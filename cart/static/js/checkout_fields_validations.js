document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("checkout-form");
    const billingSame = document.getElementById("billingSame");
    const billingDifferent = document.getElementById("billingDifferent");
    const billingWrapper = document.getElementById("billing-form-wrapper");

    // --------------------------------------------------
    // Billing toggle
    // --------------------------------------------------

    function updateBillingForm() {

        const differentBilling = billingDifferent.checked;
        billingWrapper.classList.toggle( "hidden",!differentBilling );
        const billingFields = billingWrapper.querySelectorAll( "input, select");
        
        billingFields.forEach(function (field) {
            field.disabled = !differentBilling;

            if (differentBilling) {
                field.dataset.required = "true";
            } else {
                field.dataset.required = "false";
                clearError(field);
            }
        });
    }


    billingSame.addEventListener( "change", updateBillingForm);

    billingDifferent.addEventListener( "change", updateBillingForm);


    // --------------------------------------------------
    // Error helpers
    // --------------------------------------------------

    function showError(field, message) {

        clearError(field);
        field.classList.add("border-red-500","focus:border-red-500" );
        const error = document.createElement("p");

        error.className ="checkout-field-error text-red-600 text-sm mt-1";
        error.textContent = message;
        field.parentElement.appendChild(error);
    }

    function clearError(field) {

        field.classList.remove("border-red-500","focus:border-red-500" );

        const oldError = field.parentElement.querySelector( ".checkout-field-error");

        if (oldError) {
            oldError.remove();
        }
    }

    // --------------------------------------------------
    // Validation helpers
    // --------------------------------------------------

    function isValidName(value) {
        return /^[A-Za-zÀ-ÖØ-öø-ÿ\s'-]{2,50}$/.test(
            value
        );
    }

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(
            value
        );
    }


    function isValidPhone(value) {
        const cleaned = value.replace(/[\s\-()+]/g, "");
        return /^\d{10,15}$/.test(cleaned);
    }


    function isValidPincode(value) {
        return /^\d{4,10}$/.test(value);
    }


    function isValidLocation(value) {
            return /^[A-Za-z]+(?: [A-Za-z]+)*$/.test(
            value
        );
    }


    // --------------------------------------------------
    // Validate required field
    // --------------------------------------------------

    function validateRequired(field, message) {

        if (!field || field.disabled) {
            return true;
        }
        const value = field.value.trim();
        if (!value) {

            showError( field,  message);
            return false;
        }
        clearError(field);
        return true;
    }

    // --------------------------------------------------
    // Validate name
    // --------------------------------------------------

    function validateName( field, label) {
        
        if (!validateRequired( field, `${label} is required.`)) {
            return false;
        }

        const value = field.value.trim();
        if (!isValidName(value)) {
            showError( field,`${label} must contain only letters, spaces, apostrophes or hyphens.` );
            return false;
        }

        clearError(field);
        return true;
    }

    // --------------------------------------------------
    // Validate email
    // --------------------------------------------------

    function validateEmail(field) {

        if (!validateRequired(field,"Email address is required.")) {
            return false;
        }

        const value = field.value.trim();
        if (!isValidEmail(value)) {
            showError(field, "Enter a valid email address.");
            return false;
        }
        clearError(field);
        return true;
    }


    // --------------------------------------------------
    // Validate phone
    // --------------------------------------------------

    function validatePhone(field) {

        if (!validateRequired(field, "Phone number is required.")) {
            return false;
        }

        const value = field.value.trim();
        if (!isValidPhone(value)) {
            showError( field, "Enter a valid phone number.");
            return false;
        }
        clearError(field);
        return true;
    }


    // --------------------------------------------------
    // Validate location
    // --------------------------------------------------

    function validateCity(field) {
        // console.log(label)
        if (!validateRequired( field, `City is required.`)) {
            return false;
        }
        const value = field.value.trim();

        if (!isValidLocation(value)) {
            showError( field, `Enter a valid City Name.` );
            return false;
        }

        clearError(field);
        return true;
    }

    function validateState( field) {
        if (!validateRequired( field, `State is required.`)) {
            return false;
        }
        const value = field.value.trim();

        if (!isValidLocation(value)) {
            showError( field, `Enter a valid State Name.` );
            return false;
        }

        clearError(field);
        return true;
    }


    // --------------------------------------------------
    // Validate pincode
    // --------------------------------------------------

    function validatePincode(field) {
        if (!validateRequired(field, "Postal code is required.")) {
            return false;
        }

        const value = field.value.trim();
        if (!isValidPincode(value)) {
            showError(field,"Enter a valid postal code.");
            return false;
        }
        clearError(field);
        return true;
    }


    // --------------------------------------------------
    // Validate address
    // --------------------------------------------------
    function validateAddress(field) {
        if (!validateRequired(field, "Address is required.")) {
            return false;
        }
        const value = field.value.trim();
        if (value.length < 5) {
            showError(field,"Address must be at least 5 characters." );
            return false;
        }

        if (value.length > 255) {
            showError(field, "Address cannot exceed 255 characters.");
            return false;
        }
        clearError(field);
        return true;
    }

    // --------------------------------------------------
    // Validate country
    // --------------------------------------------------

    function validateCountry(field) {

        if (!validateRequired( field, `Country is required.`)) {
            return false;
        }
        const value = field.value.trim();

        if (!isValidLocation(value)) {
            showError( field, `Enter a valid Country Name.` );
            return false;
        }

        clearError(field);

        return true;
    }

    // --------------------------------------------------
    // Shipping validation
    // --------------------------------------------------

    function validateShipping() {

        let valid = true;
        valid = validateName(document.getElementById("shippingFirstName"),"First name") && valid;
        valid = validateName( document.getElementById("shippingLastName"), "Last name") && valid;
        valid = validateAddress(document.getElementById("shippingAddress") ) && valid;
        valid = validateCity(document.getElementById("shippingCity")) && valid;
        valid = validateState( document.getElementById("shippingState")) && valid;
        valid = validatePincode( document.getElementById("shippingPostalCode") ) && valid;
        valid = validateCountry( document.getElementById("shippingCountry")) && valid;
        valid = validatePhone( document.getElementById("shippingPhone")) && valid;

        return valid;
    }


    // --------------------------------------------------
    // Billing validation
    // --------------------------------------------------

    function validateBilling() {

        if (!billingDifferent.checked) {
            return true;
        }

        let valid = true;
        valid = validateName( document.getElementById("billingFirstName"), "First name") && valid;
        valid = validateName( document.getElementById("billingLastName"),"Last name" ) && valid;
        valid = validatePhone( document.getElementById("billingPhone") ) && valid;
        valid = validateEmail( document.getElementById("billingEmail") ) && valid;
        valid = validateAddress( document.getElementById("billingAddress") ) && valid;
        valid = validateCity( document.getElementById("billingCity")) && valid;
        valid = validateState( document.getElementById("billingState") ) && valid;
        valid = validatePincode( document.getElementById("billingPincode") ) && valid;
        valid = validateCountry( document.getElementById("billingCountry") ) && valid;

        return valid;
    }


    // --------------------------------------------------
    // Form submit
    // --------------------------------------------------

    form.addEventListener("submit", function (event) {

        event.preventDefault();
        let valid = true;

        // Contact
        valid = validateEmail(document.getElementById("email")) && valid;

        // Shipping
        valid = validateShipping() && valid;

        // Billing
        valid = validateBilling() && valid;

        if (!valid) {
            const firstError = form.querySelector( ".checkout-field-error");

            if (firstError) {
                firstError.previousElementSibling?.focus();
                firstError.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            }
            return;
        }

        // Everything valid
        form.submit();

    });


    // --------------------------------------------------
    // Live validation on blur
    // --------------------------------------------------

    const fields = form.querySelectorAll("input, select");

    fields.forEach(function (field) {
        field.addEventListener("blur",function () {
                if ( field.disabled || field.type === "radio") {
                    return;
                }
                if (!field.value.trim()) {
                    return;
                }

                // Individual validation
                if (field.id === "email" || field.id === "billingEmail") {
                    validateEmail(field);
                }

                else if (field.id === "shippingFirstName" || field.id === "shippingLastName" || field.id === "billingFirstName" ||field.id === "billingLastName") {
                    validateName(
                        field,
                        field.placeholder || "Name"
                    );
                }

                else if (field.id === "phone" ||field.id === "billingPhone") {
                    validatePhone(field);
                }

                else if (field.id === "postalCode" ||field.id === "billingPincode") {
                    validatePincode(field);
                }

                else if ( field.id === "shippingAddress" || field.id === "billingAddress") {
                    validateAddress(field);
                }

                else if ( field.id === "shippingCity" || field.id === "billingCity") {
                    validateCity(field);
                }

                else if ( field.id === field.id === "shippingState" ||  field.id === "billingState") {
                    validateState(field);
                }

                else if ( field.id === "shippingCountry" || field.id === "billingCountry") {
                    validateCountry(field);
                }
            }
        );

    });

    // Initial billing state
    updateBillingForm();

});