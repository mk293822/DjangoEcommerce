document.addEventListener("DOMContentLoaded", () => {
	// Profile dropdown
	const profileDropdown = document.getElementById("profile-dropdown");
	const profileButton = document.getElementById("profile-button");

	if (profileButton && profileDropdown) {
		profileButton.addEventListener("click", () => {
			const isOpen = profileDropdown.classList.contains("opacity-100");

			profileDropdown.classList.toggle("opacity-100", !isOpen);
			profileDropdown.classList.toggle("opacity-0", isOpen);
			profileDropdown.classList.toggle("pointer-events-none", isOpen);
		});

		document.addEventListener("click", (e) => {
			if (
				!profileButton.contains(e.target) &&
				!profileDropdown.contains(e.target)
			) {
				profileDropdown.classList.remove("opacity-100");
				profileDropdown.classList.add("opacity-0", "pointer-events-none");
			}
		});
	}

	// 🔍 Search
	const searchInput = document.querySelector("[data-search-input]");
	const productList = document.querySelector("#productList");

	let debounceTimer;

	if (searchInput && productList) {
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
	}
});
