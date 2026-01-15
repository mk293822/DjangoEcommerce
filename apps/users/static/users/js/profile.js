document.addEventListener("DOMContentLoaded", () => {
	// Avatar Image edit
	const avatarInput = document.querySelector("#avatar-input");
	const avatarEditBtn = document.querySelector("#avatar-edit-btn");
	const avatarContainer = document.querySelector("#avatar-container");

	avatarEditBtn.addEventListener("click", () => {
		avatarInput.click();
	});

	avatarInput.addEventListener("change", (e) => {
		const file = e.target.files[0];
		if (!file) return;

		const img = document.createElement("img");
		img.className = "avatar-icon w-full h-full object-cover";
		img.src = URL.createObjectURL(file);
		img.alt = "User Avatar";

		avatarContainer.innerHTML = "";
		avatarContainer.appendChild(img);
	});
});
