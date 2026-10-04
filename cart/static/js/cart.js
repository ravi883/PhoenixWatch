document.addEventListener("DOMContentLoaded", function () {

    console.log("DOM loaded");
    console.log("Buttons:",document.querySelectorAll(".add-to-bag-btn").length);
    // =====================================================
    // CSRF TOKEN
    // =====================================================
    function getCSRFToken() {

        const cookie = document.cookie
            .split("; ")
            .find(
                row => row.startsWith("csrftoken=")
            );

        if (!cookie) {
            return "";
        }

        return decodeURIComponent(
            cookie.split("=")[1]
        );
    }


    // =====================================================
    // UPDATE CART COUNTER
    // =====================================================

    function updateCartCounters(count) {

        document
            .querySelectorAll(".cart-counter")
            .forEach(element => {

                element.textContent = count;

            });
    }


    // =====================================================
    // ADD TO CART
    // =====================================================

    document.querySelectorAll(".add-to-bag-btn").forEach(button => {
        button.addEventListener("click", function () {
            const productId = this.dataset.productId;
            console.log("ADD TO BAG CLICKED");

            // Optional quantity input
            const quantityInput = document.getElementById("quantity"
                );

            const quantity =quantityInput? quantityInput.value: 1;
            const formData = new FormData();
            formData.append("quantity",quantity);
            console.log(productId)

            fetch(
                `/cart/add/${productId}/`,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken":
                            getCSRFToken(),
                        "X-Requested-With":
                            "XMLHttpRequest",
                    },
                    body: formData,
                }
            )
            .then(response =>response.json())
            .then(data => {
                if (!data.success) {
                    alert(data.message);
                    return;
                }
                updateCartCounters(
                    data.cart_count
                );
                console.log(data.message);
            })
            .catch(error => {
                console.error("Add to cart error:",error)
            });
            }
        );

    });


    // =====================================================
    // UPDATE QUANTITY
    // =====================================================

    document.querySelectorAll(".quantity-btn").forEach(button => {
        button.addEventListener("click",function () {
            console.log("button clicked")

            const itemId =this.dataset.itemId;
            console.log("item_id:",itemId)

            const action =this.dataset.action;
            console.log("action:",action)

            const quantityElement =document.getElementById(`quantity-${itemId}`);
            
            console.log("quantityElement:",quantityElement)
            let quantity =parseInt(quantityElement.textContent);
            console.log("quantity:",quantity)

            if (action === "increase") {
                quantity++;
            }
            if (action === "decrease") {
                quantity--;
            }

            updateQuantity(itemId,quantity);
        });
    });


    // =====================================================
    // UPDATE QUANTITY REQUEST
    // =====================================================

    function updateQuantity(itemId,quantity) {
         const formData = new FormData();

        formData.append("quantity", quantity );
        console.log("quantity:", quantity)
        fetch(
            `/cart/update/${itemId}/`,
            {
                method: "POST",

                headers: {
                    "X-CSRFToken":
                        getCSRFToken(),

                    "X-Requested-With":
                        "XMLHttpRequest",
                },
                body: formData,
            }
        )
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(data.message);
                return;
            }

            // Item removed

            if (data.removed) {
                const cartItem =document.getElementById(`cart-item-${itemId}`);

                if (cartItem) {
                    cartItem.remove();
                }

            }
            else {
                document.getElementById(`quantity-${itemId}`).textContent =data.quantity;
                document.getElementById(`line-total-${itemId}`).textContent =data.line_total;
            }

            // Update subtotal
            const subtotal =document.getElementById( "cart-subtotal");

            if (subtotal) {
                subtotal.textContent = data.subtotal;
            }

           // Update count

            const count =document.getElementById("summary-count");
            if (count) {
                count.textContent =data.cart_count;
            }

            updateCartCounters(data.cart_count);

            // Empty cart

            if (data.cart_count === 0) {
                location.reload();
            }

        })
        .catch(error => {
            console.error("Update cart error:", error);
        });
    }


    // =====================================================
    // REMOVE ITEM
    // =====================================================

    document
        .querySelectorAll(".remove-cart-item")
        .forEach(button => {

            button.addEventListener(
                "click",
                function () {

                    const itemId =
                        this.dataset.itemId;


                    fetch(
                        `/cart/remove/${itemId}/`,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCSRFToken(),

                                "X-Requested-With":
                                    "XMLHttpRequest",
                            },
                        }
                    )
                    .then(response =>
                        response.json()
                    )
                    .then(data => {

                        if (!data.success) {

                            alert(
                                data.message
                            );

                            return;
                        }


                        const cartItem =
                            document.getElementById(
                                `cart-item-${itemId}`
                            );

                        if (cartItem) {
                            cartItem.remove();
                        }


                        document.getElementById(
                            "cart-subtotal"
                        ).textContent =
                            data.subtotal;


                        document.getElementById(
                            "summary-count"
                        ).textContent =
                            data.cart_count;


                        updateCartCounters(
                            data.cart_count
                        );


                        if (
                            data.cart_count === 0
                        ) {
                            location.reload();
                        }

                    });

                }
            );

        });


    // =====================================================
    // CLEAR CART
    // =====================================================

    const clearButton =
        document.getElementById(
            "clear-cart"
        );


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function () {

                if (
                    !confirm(
                        "Are you sure you want to clear your cart?"
                    )
                ) {
                    return;
                }


                fetch(
                    "/cart/clear/",
                    {
                        method: "POST",

                        headers: {
                            "X-CSRFToken":
                                getCSRFToken(),

                            "X-Requested-With":
                                "XMLHttpRequest",
                        },
                    }
                )
                .then(response =>
                    response.json()
                )
                .then(data => {

                    if (!data.success) {

                        alert(
                            data.message
                        );

                        return;
                    }

                    location.reload();

                });

            }
        );
    }

});