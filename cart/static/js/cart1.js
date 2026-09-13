document.addEventListener("DOMContentLoaded", function () {

    console.log("cart.js loaded");


    // =========================================================
    // CSRF TOKEN
    // =========================================================

    function getCSRFToken() {
        const csrfInput = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

        return csrfInput ? csrfInput.value : "";
    }


    // =========================================================
    // UPDATE ALL CART COUNTERS
    // =========================================================

    function updateCartCounters(count) {
        document.querySelectorAll(".cart-counter").forEach(counter => {
            counter.textContent = count;
        });
    }


    async function loadCartDrawer() {

    const drawerItems = document.getElementById("cart-drawer-items");

    if (!drawerItems) {
        console.error(
            "cart-drawer-items not found"
        );
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

    (function () {
        const cartBtns = document.querySelectorAll(".cart-toggle-btn");
        const closeCartBtn = document.getElementById("close-cart");

        const cartDrawer = document.getElementById("cart-drawer");
        const cartOverlay = document.getElementById("cart-overlay");
        const cartContent = document.getElementById("cart-content");

        function openCart() {

            if (!cartDrawer || !cartOverlay || !cartContent) {
                console.error("Cart drawer elements not found.");
                return;
            }
            // Show main drawer
            cartDrawer.classList.remove("invisible");

            // Small delay is required for CSS transition
            setTimeout(function () {

                // Show overlay
                cartOverlay.classList.add("opacity-100");

                // Slide drawer from right
                cartContent.classList.remove("translate-x-full");

            }, 10);

            // Prevent background scrolling
            document.body.style.overflow = "hidden";
        }

        // function closeCart() {
        //     if (!cartDrawer || !cartOverlay || !cartContent) {
        //         return;
        //     }
        //     // Hide overlay
        //     cartOverlay.classList.remove("opacity-100");
        //     // Slide drawer back to right
        //     cartContent.classList.add("translate-x-full");
        //     // Wait for animation
        //     setTimeout(function () {
        //         cartDrawer.classList.add("invisible");

        //         // Enable scrolling again
        //         document.body.style.overflow = "";

        //     }, 300);
        // }

        cartBtns.forEach(function (btn) {

            btn.addEventListener("click", function (event) {

                event.preventDefault();

                openCart();

            });

        });

    //     if (closeCartBtn) {

    //         closeCartBtn.addEventListener("click", function () {

    //             closeCart();

    //         });

    //     }

    //     if (cartOverlay) {

    //     cartOverlay.addEventListener("click", function () {

    //         closeCart();

    //     });

    // }


    /*
    |--------------------------------------------------------------------------
    | MAKE FUNCTIONS AVAILABLE GLOBALLY
    |--------------------------------------------------------------------------
    */

    window.openCart = openCart;
    // window.closeCart = closeCart;

})();



    // =========================================================
    // ADD TO CART
    // =========================================================

    document.querySelectorAll(".add-to-bag-btn").forEach(button => {
        button.addEventListener("click", async function () {
            const productId = this.dataset.productId;
            if (!productId) {
                console.error("Product ID not found");
                return;
            }
            
            const quantityDisplay =document.getElementById("qty-display");
            const quantity = quantityDisplay ? ( parseInt( quantityDisplay.textContent.trim(), 10 ) || 1 ) : 1;
            const formData = new FormData();
            
            formData.append("quantity", String(quantity));
            
            // Disable button while request is running
            this.disabled = true;
            try {
                const response = await fetch(
                    `/cart/add/${productId}/`,
                    {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCSRFToken(),
                            "X-Requested-With": "XMLHttpRequest",
                       },
                        body: formData,
                    }
                );

                const data = await response.json();
                console.log("Add cart response:", data);

                if (!response.ok) {
                    throw new Error(data.message ||"Unable to add product to cart.");
                }

                if (!data.success) {
                    alert(data.message ||"Unable to add product.");
                    return;
                }
                // Update header counters
                updateCartCounters(data.cart_count);

                await loadCartDrawer();
                openCart();
                
                // Button feedback
                // const originalText = this.textContent;
                // this.textContent = "Added to Bag";

                // setTimeout(() => {
                //     this.textContent = originalText;
                // }, 1500);
                }
                catch (error) {
                    console.error("Add to cart error:", error);
                    alert(error.message || "Something went wrong.");
                } finally {
                    this.disabled = false;
                }
            });
        });

    // =========================================================
    // CART PAGE - QUANTITY BUTTONS
    // =========================================================


    // =========================================================
    // UPDATE CART QUANTITY
    // =========================================================


    const quantityControls = document.querySelectorAll(".quantity-control");
    quantityControls.forEach(function (control) {
        const minusButton =control.querySelector(".quantity-minus");
        const plusButton =control.querySelector(".quantity-plus");
        const quantityValue =control.querySelector(".quantity");

        // PLUS
        plusButton.addEventListener("click", function () {
            const itemId = this.dataset.itemId;
            let quantity = parseInt(quantityValue.textContent.trim(), 10);
            quantity++;
            updateQuantity(itemId, quantity);
        });

        // MINUS
        minusButton.addEventListener("click", function () {
            const itemId = this.dataset.itemId;
            
            let quantity =parseInt(quantityValue.textContent.trim(), 10);
            if (quantity <= 1) {
                return;
            }
            quantity--;
            updateQuantity(itemId, quantity);
        });
    })
   
    async function updateQuantity(itemId, quantity) {

        const formData = new URLSearchParams();

        formData.append("quantity", quantity);

        fetch(`/cart/update/${itemId}/`, {

            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type":
                    "application/x-www-form-urlencoded",
            },

            body: formData,

        }).then(response => response.json()).then(data => {
            if (!data.success) {
                alert(data.message);
                return;
            }

            /*
             * Update quantity displayed
             */
            const quantityControl = document.querySelector(`.quantity-plus[data-item-id="${itemId}"]`)?.closest(".quantity-control");
            if (quantityControl) {
                const quantityElement = quantityControl.querySelector(".quantity");
                quantityElement.textContent = data.quantity;
            }

            /*
             * Update subtotal
             */
            const subtotalElement = document.getElementById("cart-subtotal");
            if (subtotalElement) {
                subtotalElement.textContent =`₹${data.subtotal}`;
            }

            /*
             * Update cart counter
             */
            const cartCounter = document.getElementById("cart-counter");
            if (cartCounter){
                cartCounter.textContent =  data.cart_count
            }
            // document.querySelectorAll(".cart-counter").forEach(counter => {
            //     counter.textContent = data.cart_count;
            // });
        })

        .catch(error => {
            console.error("Update cart error:", error
            );
        });
    }

    function updateCartDrawerState() {

        const cartItems = document.querySelectorAll(".cart-item");
        const cartSummary = document.getElementById("cart-summary");
        const emptyState = document.getElementById("cart-empty-state");

        if (cartItems.length === 0) {

            // Cart is empty
            cartSummary?.classList.add("hidden");
            emptyState?.classList.remove("hidden");

        } else {

            // Cart has items
            cartSummary?.classList.remove("hidden");
            emptyState?.classList.add("hidden");

        }
    }
    // =========================================================
    // REMOVE CART ITEM
    // =========================================================
    // const removeButton = document.querySelector('.remove-cart-item')

    document.querySelectorAll(".remove-cart-item").forEach(button => {
        button.addEventListener("click",async function (event) {

            event.preventDefault();
            event.stopPropagation();
            const itemId = this.dataset.itemId;
            if (!itemId) {
                console.error("Cart item ID missing");
                return;
            }
            try {
                const response = await fetch(
                                `/cart/remove/${itemId}/`,
                                {
                                    method: "POST",
                                    headers: {
                                        "X-CSRFToken":getCSRFToken(),
                                        "X-Requested-With":"XMLHttpRequest",
                                    },
                                }
                            );
                const data = await response.json();

                console.log("Remove response:", data);

                if (!response.ok || !data.success) {
                    throw new Error(
                        data.message || "Unable to remove item."
                    );
                }

                 // Remove item from DOM
                const cartItem =document.getElementById(`cart-item-${itemId}`);
                if (cartItem) {
                    cartItem.remove();
                }

                // Update cart counter
                updateCartCounters(data.cart_count);

                // Update subtotal
                const subtotalElement =document.getElementById("cart-subtotal");
                if ( subtotalElement && data.subtotal !== undefined) {
                    subtotalElement.textContent =`₹${data.subtotal}`;
                }
                 // --------------------------------
            // Check if cart is empty
            // --------------------------------

            updateCartDrawerState();
                } catch (error) {
                    console.error("Remove cart item error:",error);
                    alert(error.message ||"Something went wrong.");
                    }
            });
        });


    // =========================================================
    // CLEAR CART
    // =========================================================

    const clearCartButton = document.getElementById("clear-cart-btn");
    if (clearCartButton) {
        clearCartButton.addEventListener("click", async function () {
        try {
            const response = await fetch(
                            "/cart/clear/",
                            {
                                method: "POST",
                                headers: {
                                    "X-CSRFToken":getCSRFToken(),
                                    "X-Requested-With":"XMLHttpRequest",
                                },
                            }
                        );
                    const data = await response.json();
                    if (!response.ok) {
                        throw new Error(data.message ||"Unable to clear cart." );
                    }
                    if (!data.success) {
                        alert(data.message || "Unable to clear cart.");
                        return;
                    }
                    // Update counter
                    updateCartCounters(0);
                    // Reload cart page
                    window.location.reload();

                } catch (error) {
                    console.error("Clear cart error:",error);
                    alert(error.message || "Something went wrong.");

                }

            });

    }


});