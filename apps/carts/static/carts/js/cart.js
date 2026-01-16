import eventBus from "/static/js/event_bus.js";

document.addEventListener("DOMContentLoaded", function () {
	// Select all add-to-cart buttons
	const buttons = document.querySelectorAll(".add-to-cart");
	const dataContainer = document.getElementById("data-container");
	const quantity = document.getElementById("product-quantity");
	const loginUrl = decodeURIComponent(dataContainer.dataset.loginUrl);
	const cartUrl = decodeURIComponent(dataContainer.dataset.cartUrl);

	document.addEventListener("click", (e) => {
		if (e.target.closest(".add-to-cart")) {
			e.stopPropagation();
			e.preventDefault();
		}
	});

	buttons.forEach((button) => {
		button.addEventListener("click", function (e) {
			e.preventDefault();

			const productId = this.dataset.productId;
			const csrfToken = this.dataset.csrf;
			const urlParams = new URLSearchParams(window.location.search);

			let selectedOptions = [...urlParams.values()]
				.map(Number)
				.filter((n) => !isNaN(n));
			if (!selectedOptions.length) selectedOptions = null;

			if (!productId) {
				console.error("Button has no product ID!", this);
				return;
			}

			const context = {
				product_id: productId,
				quantity: quantity?.value ?? 1,
				selectedOptions: selectedOptions,
			};
			addToCartFetch({ context, csrfToken });
		});
	});

	const updateCartNumber = (data) => {
		if (typeof data === "string") {
			data = JSON.parse(data);
		}

		const cartItemCounts = document.querySelectorAll(".cartItemCount");
		const cartItemTotalPrice = document.querySelectorAll(".cartItemTotalPrice");
		const cartItem = document.getElementById(`cart-item-${data.cart_item.id}`);

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
				.getElementById("cartItemsContainer")
				.insertAdjacentHTML("afterbegin", data.html);
			const emptyCartContainer = document.getElementById("emptyCartContainer");
			if (emptyCartContainer) {
				emptyCartContainer.classList.add("hidden");
			}
		}
	};

	const addToCartFetch = async ({ context, csrfToken }) => {
		try {
			const res = await fetch(cartUrl, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": csrfToken,
				},
				body: JSON.stringify(context),
			});
			const data = await res.json();

			if (res.status === 401) {
				window.location.href = loginUrl;
				return;
			}

			if (!res.ok || data.status === "error") {
				eventBus.emit("notify:error", data.message);
				return;
			}

			eventBus.emit("notify:success", data.message);
			updateCartNumber(data);
		} catch (err) {
			console.error(err);
			eventBus.emit("notify:error", "Something went wrong!");
		}
	};
});
