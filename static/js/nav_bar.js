document.addEventListener("DOMContentLoaded", () => {
	const profileDropdown = document.getElementById("profile-dropdown");
	const profileButton = document.getElementById("profile-button");

	profileButton.addEventListener("click", () => {
		const isOpen = profileDropdown.classList.contains("opacity-100");

		if (isOpen) {
			profileDropdown.classList.remove("opacity-100");
			profileDropdown.classList.add("opacity-0", "pointer-events-none");
		} else {
			profileDropdown.classList.remove("opacity-0", "pointer-events-none");
			profileDropdown.classList.add("opacity-100");
		}
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
});
