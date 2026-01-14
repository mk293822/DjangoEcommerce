document.addEventListener("DOMContentLoaded", () => {
	const setupDropdown = (buttonId, dropdownId) => {
		const button = document.querySelector(`#${buttonId}`);
		const dropdown = document.querySelector(`#${dropdownId}`);

		if (!button || !dropdown) return;

		// Toggle dropdown when clicking the button
		button.addEventListener("click", (e) => {
			e.stopPropagation();

			// Close all other dropdowns
			document.querySelectorAll(".dropdown").forEach((dd) => {
				if (dd !== dropdown) {
					dd.classList.remove("opacity-100");
					dd.classList.add("opacity-0", "pointer-events-none");
				}
			});

			const isOpen = dropdown.classList.contains("opacity-100");

			dropdown.classList.toggle("opacity-100", !isOpen);
			dropdown.classList.toggle("opacity-0", isOpen);
			dropdown.classList.toggle("pointer-events-none", isOpen);
		});

		// Close dropdown when clicking outside
		document.addEventListener("click", (e) => {
			if (!dropdown.contains(e.target) && !button.contains(e.target)) {
				dropdown.classList.remove("opacity-100");
				dropdown.classList.add("opacity-0", "pointer-events-none");
			}
		});
	};

	// Setup both dropdowns
	setupDropdown("profile-button", "profile-dropdown");
	setupDropdown("cart-button", "cart-dropdown");
	// 🔍 Search
	const searchInputs = document.querySelectorAll("[data-search-input]");
	const productList = document.querySelector("#productList");

	let debounceTimer;

	if (searchInputs && productList) {
		searchInputs.forEach((searchInput) => {
			searchInput.addEventListener("input", (e) => {
				clearTimeout(debounceTimer);

				debounceTimer = setTimeout(() => {
					query = e.target.value;
					const params = new URLSearchParams(window.location.search);
					if (query) {
						params.set("q", query);
					} else {
						params.delete("q");
					}
					const url = `${window.location.pathname}?${params.toString()}`;

					fetch(url, {
						headers: { "X-Requested-With": "XMLHttpRequest" },
					})
						.then((res) => res.text())
						.then((html) => {
							productList.innerHTML = html;
						});

					history.replaceState(null, "", url);
				}, 300); // 300ms debounce
			});
		});
	}
});
