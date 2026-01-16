document.addEventListener("DOMContentLoaded", () => {
	/* ===============================
	 * 1. READ DATA FROM DJANGO
	 * =============================== */

	// { Color: 15, Size: 18, Storage: 21 }
	let selectedVariationOptions = JSON.parse(
		document.getElementById("selected_options_data").textContent
	);

	// {
	//   "12": { stock: 10, price: 199, variation_type_options: [15,18,21] },
	//   "13": { stock: 5,  price: 209, variation_type_options: [15,18,22] }
	// }
	const productVariationMap = JSON.parse(
		document.getElementById("product_variations_data").textContent
	);

	/* ===============================
	 * 2. DOM ELEMENTS
	 * =============================== */
	const carouselWrapper = document.querySelector("#carousel-container");
	const productQuantity = document.querySelector("#product-quantity");
	const productPrice = document.querySelector("#product-price");
	const imageVariationButtons = document.querySelectorAll(
		".variation-image-btn"
	);
	const radioVariationInputs = document.querySelectorAll(".radio-btn");
	const selectVariationInputs = document.querySelectorAll(".variation-select");

	const urlParams = new URLSearchParams(window.location.search);
	const currentPath = window.location.pathname;
	const addToCartBtn = document.querySelector("#product-show-add-to-cart-btn");
	/* ===============================
	 * 3. PREPARE VARIATION MATRIX
	 * =============================== */
	// [[15,18,21], [15,18,22], ...]
	const variationCombinations = Object.values(productVariationMap).map(
		(variation) => variation.variation_type_options
	);

	const normalizeCombination = (arr) => arr.slice().sort().join("-");

	const validVariationSet = new Set(
		variationCombinations.map(normalizeCombination)
	);

	function isVariationOptionValid(
		optionId,
		optionType,
		currentSelections = selectedVariationOptions
	) {
		const selectedIds = Object.entries(currentSelections)
			.filter(([key]) => key !== optionType)
			.map(([, value]) => Number(value));

		const testCombination = normalizeCombination([
			...selectedIds,
			Number(optionId),
		]);

		return validVariationSet.has(testCombination);
	}

	/* ===============================
	 * 4. UPDATE OPTION STATES
	 * =============================== */
	function updateVariationAvailability() {
		// IMAGE VARIATIONS
		imageVariationButtons.forEach((btn) => {
			const dataSet = btn.dataset;

			const disabled = !isVariationOptionValid(
				dataSet.imageId,
				dataSet.imageType
			);

			btn.disabled = disabled;
			btn.classList.toggle("opacity-40", disabled);
			btn.classList.toggle("cursor-not-allowed", disabled);
		});

		// RADIO VARIATIONS
		radioVariationInputs.forEach((input) => {
			input.disabled = !isVariationOptionValid(
				input.dataset.optionId,
				input.name
			);
		});

		// SELECT VARIATIONS
		selectVariationInputs.forEach((select) => {
			select.querySelectorAll("option").forEach((option) => {
				option.disabled = !isVariationOptionValid(
					option.value,
					select.dataset.optionType
				);
			});
		});
	}

	/* ===============================
	 * 5. IMAGE VARIATIONS
	 * =============================== */
	imageVariationButtons.forEach((btn) => {
		const imageOptionId = btn.dataset.imageId;
		const variationType = btn.dataset.imageType;

		// restore selected state
		if (selectedVariationOptions[variationType] == imageOptionId) {
			btn.classList.add("border-fuchsia-700");
		}

		let fetchDebounceTimer;

		btn.addEventListener("click", () => {
			if (btn.disabled) return;

			clearTimeout(fetchDebounceTimer);

			selectedVariationOptions[variationType] = Number(imageOptionId);
			urlParams.set(variationType, imageOptionId);

			const nextUrl = `${currentPath}?${urlParams.toString()}`;

			fetchDebounceTimer = setTimeout(() => {
				fetch(nextUrl, {
					headers: { "X-Requested-With": "XMLHttpRequest" },
				})
					.then((res) => res.text())
					.then((html) => {
						window.history.replaceState({}, "", nextUrl);
						carouselWrapper.innerHTML = html;

						imageVariationButtons.forEach((b) =>
							b.classList.remove("border-fuchsia-700")
						);
						btn.classList.add("border-fuchsia-700");
						updatePriceAndQuantity();
						updateVariationAvailability();
					});
			}, 300);
		});
	});

	/* ===============================
	 * 6. RADIO VARIATIONS
	 * =============================== */
	radioVariationInputs.forEach((input) => {
		const optionId = input.dataset.optionId;
		const variationType = input.name;

		if (selectedVariationOptions[variationType] == optionId) {
			input.checked = true;
		}

		input.addEventListener("change", () => {
			if (input.disabled) return;

			selectedVariationOptions[variationType] = Number(optionId);
			urlParams.set(variationType, optionId);

			window.history.replaceState(
				{},
				"",
				`${currentPath}?${urlParams.toString()}`
			);
			updatePriceAndQuantity();
			updateVariationAvailability();
		});
	});

	/* ===============================
	 * 7. SELECT VARIATIONS
	 * =============================== */
	selectVariationInputs.forEach((select) => {
		const variationType = select.dataset.optionType;

		if (selectedVariationOptions[variationType]) {
			select.value = selectedVariationOptions[variationType];
		}

		select.addEventListener("change", (e) => {
			selectedVariationOptions[variationType] = Number(e.target.value);
			urlParams.set(variationType, e.target.value);

			window.history.replaceState(
				{},
				"",
				`${currentPath}?${urlParams.toString()}`
			);
			updatePriceAndQuantity();
			updateVariationAvailability();
		});
	});

	/* ===============================
	 * 8. SET QUANTITY AND PRICE
	 * =============================== */
	function updatePriceAndQuantity() {
		if (selectedVariationOptions) {
			const selectedProductVariation = Object.values(productVariationMap).find(
				(variation) =>
					normalizeCombination(variation.variation_type_options) ===
					normalizeCombination(
						Object.values(selectedVariationOptions).map(Number)
					)
			);

			productPrice.innerHTML = `$${selectedProductVariation?.price ?? 0}`;
			const stock = selectedProductVariation?.stock ?? 0;
			const end = Math.min(stock, 10);
			const disabled = stock < 1;

			addToCartBtn.disabled = disabled;
			productQuantity.innerHTML = "";

			if (disabled) {
				const option = document.createElement("option");
				option.text = "Quantity: 0";
				option.value = 0;
				option.disabled = true;
				productQuantity.add(option);
				productQuantity.value = 0;
			} else {
				for (let i = 1; i <= end; i++) {
					const option = document.createElement("option");
					option.value = i;
					option.text = `Quantity: ${i}`;
					option.classList.add("bg-slate-700");
					productQuantity.add(option);
				}
			}
		}
	}

	/* ===============================
	 * 9. INITIAL STATE
	 * =============================== */
	updatePriceAndQuantity();
	updateVariationAvailability();
});
