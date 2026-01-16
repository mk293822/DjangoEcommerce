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

	// Delete Account
	// Elements
	const deleteAccountBtn = document.getElementById("delete-account-btn");
	const deleteAccountModal = document.getElementById("delete-account-modal");
	const deleteAccountModalPasswordConfirm = document.getElementById(
		"delete-account-model-password-confirm"
	);
	const deleteAccountModalCancelBtn = document.getElementById(
		"delete-account-model-cancel-btn"
	);
	const deleteAccountModalSubmitBtn = document.getElementById(
		"delete-account-model-submit-btn"
	);

	// Initial state
	deleteAccountModalSubmitBtn.disabled = true;

	// Open modal
	deleteAccountBtn.addEventListener("click", () => {
		deleteAccountModal.classList.remove("hidden");
		deleteAccountModal.classList.add("flex");
		deleteAccountModalPasswordConfirm.value = "";
		deleteAccountModalSubmitBtn.disabled = true;
	});

	// Cancel modal
	deleteAccountModalCancelBtn.addEventListener("click", () => {
		deleteAccountModal.classList.add("hidden");
		deleteAccountModal.classList.remove("flex");
	});

	// Enable/disable submit based on input
	deleteAccountModalPasswordConfirm.addEventListener("input", (e) => {
		deleteAccountModalSubmitBtn.disabled = !e.target.value;
	});

	// Submit modal
	deleteAccountModalSubmitBtn.addEventListener("click", () => {
		if (deleteAccountModalPasswordConfirm.value) {
			// Here you can call API or form submission
			deleteAccountModal.classList.add("hidden");
			deleteAccountModal.classList.remove("flex");
		}
	});
});
