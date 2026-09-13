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
                alert(data.message || "Unable to update cart.");
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

        } catch (error) {

            console.error("Cart update error:", error);

            alert("Something went wrong. Please try again.");
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

                alert(data.message || "Unable to remove item.");

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


            // Check if cart is empty
            checkEmptyCart();


        } catch (error) {

            console.error("Remove cart item error:", error);

            alert("Something went wrong. Please try again.");

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
                alert(
                    data.message ||
                    "Unable to add product to cart."
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
            alert("Something went wrong. Please try again.");
        } finally {
            addButton.disabled = false;
        }

    });

});