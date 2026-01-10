// Listen for ALL click events on the document
// (event delegation – works even if buttons are added dynamically)
document.addEventListener("click", (e) => {
	// Find the closest element with class ".carousel-btns"
	// This allows clicks on child elements (like <img>)
	const btn = e.target.closest(".carousel-btns");
	if (!btn) return; // click was not on a carousel button

	// Find the parent carousel container
	const carousel = btn.closest("#product-carousel");
	if (!carousel) return; // safety check

	// Get the main carousel image element
	const carouselImg = carousel.querySelector("#carousel-img");

	// Get all carousel buttons inside this carousel
	const carouselBtns = carousel.querySelectorAll(".carousel-btns");

	if (!carouselImg) return; // no image found → stop

	/* ===============================
	 * Update main image
	 * =============================== */
	// Change the main image source to the clicked thumbnail image
	carouselImg.src = btn.dataset.image;

	/* ===============================
	 * Update active border
	 * =============================== */
	// Remove active border from all buttons
	carouselBtns.forEach((b) => b.classList.remove("border-fuchsia-700"));

	// Add active border to the clicked button
	btn.classList.add("border-fuchsia-700");
});
