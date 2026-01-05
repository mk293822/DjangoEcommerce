document.addEventListener("DOMContentLoaded", function () {
	// Select all add-to-cart buttons
	const buttons = document.querySelectorAll(".add-to-cart");
	const productList = document.querySelector("#productList");
	const csrfToken = productList.dataset.csrf;
	const loginUrl = decodeURIComponent(productList.dataset.loginUrl);
	const isAuthenticated = productList.dataset.auth;
	const cartUrl = decodeURIComponent(productList.dataset.cartUrl);

	document.addEventListener("click", (e) => {
		if (e.target.closest(".add-to-cart")) {
			e.preventDefault();
			e.stopPropagation();
		}
	});

	buttons.forEach((button) => {
		button.addEventListener("click", function (e) {
			e.preventDefault();
			const productId = this.dataset.productId; // this must exist

			if (!productId) {
				console.error("Button has no product ID!", this);
				return;
			}

			if (isAuthenticated) {
				fetch(cartUrl, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-CSRFToken": csrfToken,
					},
					body: JSON.stringify({ product_id: productId }),
				})
					.then((res) => res.text())
					.then((data) => {
						updateCartNumber(data);
					});
			} else {
				window.location.href = loginUrl;
			}
		});
	});

	const updateCartNumber = (data) => {
		if (typeof data === "string") {
			data = JSON.parse(data);
		}

		if (data.status == "success") {
			const cartItemCounts = document.querySelectorAll(".cartItemCount");
			const cartItemTotalPrice = document.querySelectorAll(
				".cartItemTotalPrice"
			);
			const cartItem = document.querySelector(
				`#cart-item-${data.cart_item.id}`
			);

			cartItemCounts.forEach((item) => (item.innerHTML = data.cart_item_count));
			cartItemTotalPrice.forEach(
				(item) => (item.innerHTML = data.cart_item_total_price)
			);

			if (cartItem) {
				const cartItemEachCount = cartItem.querySelector(".cartItemEachCount");
				if (cartItemEachCount)
					cartItemEachCount.innerHTML = data.cart_item.quantity;
			} else if (data.html) {
				document
					.querySelector("#cartItemsContainer")
					.insertAdjacentHTML("afterbegin", data.html);
				const emptyCartContainer = document.querySelector(
					"#emptyCartContainer"
				);
				if (emptyCartContainer) {
					emptyCartContainer.classList.add("hidden");
				}
			}
		}
	};
});
