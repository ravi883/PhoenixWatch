document.addEventListener("DOMContentLoaded", function () {
    // =========================================================
    // CSRF TOKEN
    // =========================================================

    function getCSRFToken() {
        const csrfInput = document.querySelector(
            'input[name="csrfmiddlewaretoken"]'
        );

        return csrfInput ? csrfInput.value : "";
    }


    // =========================================================
    // CART ELEMENTS
    // =========================================================

    const cartDrawer = document.getElementById("cart-drawer");
    const cartOverlay = document.getElementById("cart-overlay");
    const cartContent = document.getElementById("cart-content");
    const cartItemsContainer = document.getElementById("cart-drawer-items");
    const cartPageItemsContainer = document.getElementById("cart-page-items");
    const cartCounter = document.getElementById("cart-counter");

    // =========================================================
    // OPEN CART
    // =========================================================

    function openCart() {
        if (!cartDrawer) return;
        cartDrawer.classList.remove("invisible");
        setTimeout(function () {
            if (cartOverlay) {
                cartOverlay.classList.add("opacity-100");
            }
            if (cartContent) {
                cartContent.classList.remove("translate-x-full");
            }
        }, 10);
        document.body.style.overflow = "hidden";
    }


    // =========================================================
    // CLOSE CART
    // =========================================================

    function closeCart() {
        if (!cartDrawer) return;
        if (cartOverlay) {
            cartOverlay.classList.remove("opacity-100");
        }
        if (cartContent) {
            cartContent.classList.add("translate-x-full");
        }
        setTimeout(function () {
            cartDrawer.classList.add("invisible");
            document.body.style.overflow = "";
        }, 300);
    }


    // =========================================================
    // CART TOGGLE BUTTONS
    // =========================================================

    document.querySelectorAll(".cart-toggle-btn").forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            openCart();
        });

    });


    // =========================================================
    // CLOSE BUTTON
    // =========================================================

    const closeCartButton =document.getElementById("close-cart");
    if (closeCartButton) {
        closeCartButton.addEventListener("click", function (event) {
            event.preventDefault();
            closeCart();
        });
    }


    // =========================================================
    // OVERLAY CLICK
    // =========================================================

    if (cartOverlay) {
        cartOverlay.addEventListener("click", function () {
            closeCart();
        });

    }

    // =========================================================
    // UPDATE CART COUNTER
    // =========================================================

    function updateCartCounter(count) {
        if (!cartCounter) return;
        cartCounter.textContent = count;
        if (parseInt(count) > 0) {
            cartCounter.classList.remove("hidden");
        } else {
            cartCounter.classList.add("hidden");
        }
    }


    // =========================================================
    // UPDATE SUBTOTAL
    // =========================================================

    function updateSubtotal(subtotal) {
        const subtotalElement = document.getElementById("cart-subtotal");
        if (!subtotalElement)
             return;
        subtotalElement.textContent = "₹ " + subtotal;
    }

    function updateTotal(itemId,total) {
        const totalElements = document.getElementById(`cart-total-${itemId}`);
        if (totalElements) {
             totalElements.textContent = "₹ " + total;
        }
    }

    function updateCartSummary(subtotal,  advance_amount, remaining_amount) {
        const subtotalElement = document.getElementById("cart-subtotal");
        const advanceElement = document.getElementById("advance-payment");
        const remainingElement = document.getElementById("remaining-payment");

        if (subtotalElement) {
            subtotalElement.textContent = "₹ " + subtotal;
        }

        if (advanceElement) {
            advanceElement.textContent = "₹ " + advance_amount;
        }

        if (remainingElement) {
            remainingElement.textContent = "₹ " + remaining_amount;
        }
    }
    // =========================================================
    // UPDATE QUANTITY
    // =========================================================

    async function updateCartQuantity(itemId, quantity, quantityElement) {
        if (!itemId) return;
        try {
            const formData = new FormData();
            formData.append("quantity", quantity);

            const response = await fetch(
                `/cart/update/${itemId}/`,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                }
            );

            const data = await response.json();
            if (!response.ok || !data.success) {
                // alert(data.message || "Unable to update cart.");
                showToast(data.message,"error","Unable to update cart.")
                return;
            }

            // Update quantity
            if (quantityElement) {
                quantityElement.textContent = data.quantity;
            }

            // Update counter
            updateCartCounter(data.cart_count);

            // Update subtotal
            updateSubtotal(data.subtotal);

            updateTotal(data.id, data.line_total);

            updateCartSummary(data.subtotal, data.advance_amount, data.remaining_amount)

        } catch (error) {

            console.error("Cart update error:", error);

            
            showToast("Something went wrong. Please try again.","error");
        }

    }


    // =========================================================
    // REMOVE CART ITEM
    // =========================================================

    async function removeCartItem(itemId, itemElement) {

        if (!itemId) return;


        try {

            const response = await fetch(
                `/cart/remove/${itemId}/`,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    }
                }
            );


            const data = await response.json();


            if (!response.ok || !data.success) {

                // alert(data.message || "Unable to remove item.");
                showToast(data.message,"error", "Unable to remove item.");

                return;
            }


            // Remove item from DOM immediately
            if (itemElement) {

                itemElement.remove();

            }


            // Update counter
            updateCartCounter(data.cart_count);


            // Update subtotal
            updateSubtotal(data.subtotal);

            updateTotal(data.id, data.total);

            updateCartSummary(data.subtotal, data.advance_amount, data.remaining_amount)
            // Check if cart is empty
            checkEmptyCart();


        } catch (error) {

            console.error("Remove cart item error:", error);

            // alert("Something went wrong. Please try again.");
            showToast("Something went wrong. Please try again.","error");

        }

    }


    // =========================================================
    // CHECK EMPTY CART
    // =========================================================

    function checkEmptyCart() {

        if (!cartItemsContainer) return;


        const cartItems =
            cartItemsContainer.querySelectorAll(".cart-item");


        if (cartItems.length === 0) {

            cartItemsContainer.innerHTML = `
                <div class="flex-1 flex items-center justify-center">

                    <div class="text-center px-6 w-full">

                        <p class="text-secondary mb-6">
                            Your cart is empty.
                        </p>

                        <a href="/">
                            <button
                                type="button"
                                class="w-full bg-primary text-on-primary font-label-caps text-label-caps py-4 rounded hover:bg-primary/90 transition-colors">
                                RETURN TO SHOP
                            </button>
                        </a>

                    </div>

                </div>
            `;
        }

    }

    function showToast(message, type = "info", title = null) {
    const container = document.getElementById("toast-container");

    if (!container) {
        console.error("Toast container not found.");
        return;
    }

    const toast = document.createElement("div");

    const config = {
        success: {
            title: title || "Success",
            icon: "✓"
        },
        error: {
            title: title || "Error",
            icon: "!"
        },
        warning: {
            title: title || "Warning",
            icon: "!"
        },
        info: {
            title: title || "Info",
            icon: "i"
        }
    };

    const current = config[type] || config.info;

    toast.className = `toast toast-${type}`;

    toast.innerHTML = `
        <div class="toast-icon">
            ${current.icon}
        </div>

        <div class="toast-content">
            <div class="toast-title">
                ${current.title}
            </div>

            <div class="toast-message">
                ${message}
            </div>
        </div>
    `;

    container.appendChild(toast);

    // Remove after animation
    setTimeout(() => {
        toast.remove();
    }, 4100);
}

    // =========================================================
    // EVENT DELEGATION
    // =========================================================
    // IMPORTANT:
    // Cart items AJAX thi change thay che.
    // Etle direct addEventListener use nahi karvu.
    // Container par ek listener rakhiye.

    if (cartItemsContainer) {

        cartItemsContainer.addEventListener("click",async function (event) {
                // =================================================
                // PLUS BUTTON
                // =================================================

                const plusButton = event.target.closest(".quantity-plus");
                if (plusButton) {
                    event.preventDefault();
                    event.stopPropagation();

                    const itemId = plusButton.dataset.itemId;
                    const quantityControl = plusButton.closest(".quantity-control");
                    if (!quantityControl) return;

                    const quantityElement = quantityControl.querySelector(".quantity");
                    if (!quantityElement) return;
                    let currentQuantity = parseInt(quantityElement.textContent.trim());

                    if (isNaN(currentQuantity)) {
                        currentQuantity = 1;
                    }
                    const maxQuantity = 5;
                    if (currentQuantity >= maxQuantity) {
                        return;
                    }

                    const newQuantity = currentQuantity + 1;

                    // Disable button during request
                    plusButton.disabled = true;

                    await updateCartQuantity(itemId, newQuantity, quantityElement );
                    plusButton.disabled = false;
                    return;
                }


                // =================================================
                // MINUS BUTTON
                // =================================================

                const minusButton = event.target.closest(".quantity-minus");
                if (minusButton) {
                    event.preventDefault();
                    event.stopPropagation();

                    const itemId = minusButton.dataset.itemId;
                    const quantityControl = minusButton.closest(".quantity-control");
                    if (!quantityControl) return;

                    const quantityElement = quantityControl.querySelector(".quantity");
                    if (!quantityElement) return;

                    let currentQuantity = parseInt( quantityElement.textContent.trim());

                    if (isNaN(currentQuantity)) {
                        currentQuantity = 1;
                    }
                    const minQuantity = 1;
                    if (currentQuantity <= minQuantity) {
                        return;
                    }
                    const newQuantity = currentQuantity - 1;
                    // Disable button during request
                    minusButton.disabled = true;

                    await updateCartQuantity(itemId,  newQuantity, quantityElement);
                    minusButton.disabled = false;
                    return;
                }


                // =================================================
                // REMOVE BUTTON
                // =================================================

                const removeButton = event.target.closest(".remove-cart-item");

                if (removeButton) {
                    event.preventDefault();
                    event.stopPropagation();

                    const itemId = removeButton.dataset.itemId;
                    if (!itemId) {
                        console.error( "Cart item ID missing" );
                        return;
                    }

                    const itemElement = removeButton.closest('[id^="cart-item-"]');
                    removeButton.disabled = true;

                    await removeCartItem(itemId, itemElement);
                    removeButton.disabled = false;
                    return;
                }
            });
        }

    if (cartPageItemsContainer) {
    cartPageItemsContainer.addEventListener("click", async function (event) {

        const plusButton = event.target.closest(".quantity-plus");

        if (plusButton) {
            event.preventDefault();

            const itemId = plusButton.dataset.itemId;
            const quantityControl = plusButton.closest(".quantity-control");
            const quantityElement = quantityControl.querySelector(".quantity");
            let currentQuantity = parseInt(quantityElement.textContent.trim());
            const newQuantity = currentQuantity + 1;

            await updateCartQuantity(itemId, newQuantity, quantityElement);
            return;
        }


        const minusButton = event.target.closest(".quantity-minus");

        if (minusButton) {
            event.preventDefault();

            const itemId = minusButton.dataset.itemId;
            const quantityControl = minusButton.closest(".quantity-control");
            const quantityElement = quantityControl.querySelector(".quantity");
            let currentQuantity = parseInt(quantityElement.textContent.trim());

            if (currentQuantity <= 1) {
                return;
            }
            const newQuantity = currentQuantity - 1;
            await updateCartQuantity(itemId, newQuantity, quantityElement);

            return;
        }


        const removeButton = event.target.closest(".remove-cart-item");

        if (removeButton) {
            event.preventDefault();
            const itemId = removeButton.dataset.itemId;
            const itemElement = removeButton.closest(".cart-item");

            await removeCartItem(itemId, itemElement);
            return;
        }

    });
}
    async function loadCartDrawer() {

    const drawerItems = document.getElementById("cart-drawer-items");
    if (!drawerItems) {
        return;
    }
    try {
        const response = await fetch(
            `/cart/drawer/`,
            {
                method: "GET",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
            }
        );

        if (!response.ok) {
            throw new Error(
                "Unable to load cart."
            );
        }

        const html = await response.text();
        drawerItems.innerHTML = html;

    } catch (error) {
        console.error(
            "Cart drawer loading error:",
            error
        );
    }
}


    // =========================================================
    // ADD TO CART
    // =========================================================

    document.addEventListener("click",async function (event) {
        const addButton = event.target.closest(".add-to-bag-btn");
        if (!addButton) return;
        event.preventDefault();
        const productId = addButton.dataset.productId;

        if (!productId) {
            console.error("Product ID missing." );
            return;
        }

        // Product page quantity
        const quantityDisplay = document.getElementById("qty-display");
        let quantity = 1;

        if (quantityDisplay) {
            quantity = parseInt(quantityDisplay.textContent.trim());
            if (isNaN(quantity) || quantity < 1) {
                quantity = 1;
            }
        }

        try {
            addButton.disabled = true;
            const formData = new FormData();
            formData.append("quantity", quantity);
            const response = await fetch(
                `/cart/add/${productId}/`,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: formData
                }
            );
            const data = await response.json();

            if (!response.ok || !data.success) {
                showToast(
                    data.message ||
                    "Unable to add product to cart.",
                    "error",
                    "Unable to Add"
                );
                return;
            }

            // Update counter
            updateCartCounter( data.cart_count);

            await loadCartDrawer();
            // Update subtotal
            updateSubtotal(data.subtotal);

            // Open drawer
            openCart();

        } catch (error) {

            console.error("Add to cart error:", error);
            // alert("Something went wrong. Please try again.");
            showToast("Something went wrong. Please try again.","error","Unable to Add");
        } finally {
            addButton.disabled = false;
        }

    });

});