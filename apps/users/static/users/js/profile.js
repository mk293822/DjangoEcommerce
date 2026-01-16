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

	deleteAccountModalSubmitBtn.disabled = true;

	deleteAccountBtn.addEventListener("click", () => {
		deleteAccountModal.classList.remove("hidden");
		deleteAccountModal.classList.add("flex");
		deleteAccountModalPasswordConfirm.value = "";
		deleteAccountModalSubmitBtn.disabled = true;
	});

	deleteAccountModalCancelBtn.addEventListener("click", () => {
		deleteAccountModal.classList.add("hidden");
		deleteAccountModal.classList.remove("flex");
	});

	deleteAccountModalPasswordConfirm.addEventListener("input", (e) => {
		deleteAccountModalSubmitBtn.disabled = !e.target.value;
	});

	// Vendor Apply
	const applyVendorBtns = document.querySelectorAll(".apply-vendor-btn");
	const applyVendorModal = document.getElementById("apply-vendor-modal");
	const applyVendorModalCancelBtn = document.getElementById(
		"apply-vendor-modal-cancel-btn"
	);

	applyVendorBtns.forEach((btn) =>
		btn.addEventListener("click", () => {
			applyVendorModal.classList.remove("hidden");
			applyVendorModal.classList.add("flex");
		})
	);

	applyVendorModalCancelBtn.addEventListener("click", () => {
		applyVendorModal.classList.add("hidden");
		applyVendorModal.classList.remove("flex");
	});

	// Vendor Details Update
	const vendorDetailsUpdateBtn = document.getElementById(
		"vendor-details-update-btn"
	);
	vendorDetailsUpdateBtn.disabled = true;
	const storeName = document.getElementById("store_name");
	const storeAddress = document.getElementById("store_address");

	let orgStoreName = storeName.value;
	let orgStoreAddress = storeAddress.value;

	storeName.addEventListener("input", (e) =>
		orgStoreName === e.target.value && orgStoreAddress === storeAddress.value
			? (vendorDetailsUpdateBtn.disabled = true)
			: (vendorDetailsUpdateBtn.disabled = false)
	);
	storeAddress.addEventListener("input", (e) =>
		orgStoreAddress === e.target.value && orgStoreName === storeName.value
			? (vendorDetailsUpdateBtn.disabled = true)
			: (vendorDetailsUpdateBtn.disabled = false)
	);
});
