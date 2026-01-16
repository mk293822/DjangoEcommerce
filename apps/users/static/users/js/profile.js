document.addEventListener("DOMContentLoaded", () => {
	// Avatar Image edit
	const avatarInput = document.getElementById("avatar-input");
	const avatarEditBtn = document.getElementById("avatar-edit-btn");
	const avatarContainer = document.getElementById("avatar-container");

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

	// Update Password
	const passwordUpdateSubmitBtn = document.getElementById(
		"password-update-submit-btn"
	);
	const passwordConfirm = document.getElementById("password-confirm");
	const newPassword = document.getElementById("new-password");
	passwordUpdateSubmitBtn.disabled = true;

	passwordConfirm.addEventListener("input", (e) => {
		if (newPassword.value === e.target.value) {
			passwordUpdateSubmitBtn.disabled = false;
		} else {
			passwordUpdateSubmitBtn.disabled = true;
		}
	});
});
