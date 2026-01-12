import eventBus from "/static/js/event_bus.js";

document.addEventListener("DOMContentLoaded", function () {
	// Select all add-to-cart buttons
	const buttons = document.querySelectorAll(".add-to-cart");
	const dataContainer = document.querySelector("#data-container");
	const loginUrl = decodeURIComponent(dataContainer.dataset.loginUrl);
	const isAuthenticated = dataContainer.dataset.auth;
	const cartUrl = decodeURIComponent(dataContainer.dataset.cartUrl);

	document.addEventListener("click", (e) => {
		if (e.target.closest(".add-to-cart")) {
			e.preventDefault();
			e.stopPropagation();
		}
	});

	buttons.forEach((button) => {
		button.addEventListener("click", function (e) {
			e.preventDefault();
			const quantity = document.querySelector("#product-quantity");
			const productId = this.dataset.productId;
			const csrfToken = this.dataset.csrf;
			const urlParams = new URLSearchParams(window.location.search);

			const selectedOptions =
				[...urlParams.values()].map(Number) == [NaN]
					? [...urlParams.values()].map(Number)
					: null;

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
					body: JSON.stringify({
						product_id: productId,
						quantity: quantity?.value ?? 1,
						selectedOptions: selectedOptions,
					}),
				})
					.then((res) => res.text())
					.then((data) => {
						if (typeof data === "string") {
							data = JSON.parse(data);
						}
						if (data.status == "success") {
							eventBus.emit("notify:success", data.message);
							// eventBus.emit("cart:updated", data);
							updateCartNumber(data);
						} else {
							eventBus.emit("notify:error", data.message);
						}
					})
					.catch((err) =>
						eventBus.emit("notify:error", "Something went wrong!")
					);
			} else {
				window.location.href = loginUrl;
			}
		});
	});

	const updateCartNumber = (data) => {
		if (typeof data === "string") {
			data = JSON.parse(data);
		}

		const cartItemCounts = document.querySelectorAll(".cartItemCount");
		const cartItemTotalPrice = document.querySelectorAll(".cartItemTotalPrice");
		const cartItem = document.querySelector(`#cart-item-${data.cart_item.id}`);

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
			const emptyCartContainer = document.querySelector("#emptyCartContainer");
			if (emptyCartContainer) {
				emptyCartContainer.classList.add("hidden");
			}
		}
	};
});
