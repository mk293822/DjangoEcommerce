document.addEventListener("DOMContentLoaded", function () {
	// Select all add-to-cart buttons
	const buttons = document.querySelectorAll(".add-to-cart");

	buttons.forEach((button) => {
		button.addEventListener("click", function () {
			const productId = this.dataset.productId; // this must exist

			if (!productId) {
				console.error("Button has no product ID!", this);
				return;
			}

			if (isAuthenticated) {
				fetch("/cart/add/", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": csrfToken,
					},
					body: JSON.stringify({ product_id: productId }),
				})
					.then((res) => {
						if (res.ok) alert("Product added to cart!");
						else alert("Failed to add product to cart.");
					})
					.then((data) => {
						console.log(data);
					});
			} else {
				window.location.href = loginUrl;
			}
		});
	});
});
