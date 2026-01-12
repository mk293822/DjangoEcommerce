import eventBus from "./event_bus.js";

const containerId = "toast-container";
const MAX_TOASTS = 3;
const DURATION = Number(document.body.dataset.toastDuration) || 3000;

const TYPES = {
	success: {
		icon: "✔️",
		border: "border-green-500",
		bg: "bg-green-50 text-green-800 dark:bg-green-900/90 dark:text-green-200",
	},
	error: {
		icon: "❌",
		border: "border-red-500",
		bg: "bg-red-50 text-red-800 dark:bg-red-900/90 dark:text-red-200",
	},
};

function createToast(message, type) {
	const cfg = TYPES[type];

	const toast = document.createElement("div");
	toast.className = "translate-x-10 opacity-0 transition-all duration-300";

	toast.innerHTML = `
        <div class="flex items-start gap-3 rounded-lg border-l-4 p-4 shadow-lg ${
					cfg.border
				} ${cfg.bg}">
            <div class="mt-1 text-xl">${cfg.icon}</div>
            <div class="flex-1">
                <p class="font-semibold">${type.toUpperCase()}</p>
                <p class="text-sm opacity-90">${message}</p>
            </div>
            <button class="toast-close text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">✕</button>
        </div>
    `;

	return toast;
}

function showToast(message, type = "success") {
	const container = document.getElementById(containerId);
	if (!container) return;

	// Remove oldest toast if over limit
	if (container.children.length >= MAX_TOASTS) {
		container.lastElementChild.remove();
	}

	const toast = createToast(message, type);
	container.prepend(toast);

	// Animate in
	requestAnimationFrame(() => {
		toast.classList.remove("translate-x-10", "opacity-0");
	});

	// Auto remove
	let timeout = setTimeout(() => removeToast(toast), DURATION);

	toast.addEventListener("mouseenter", () => clearTimeout(timeout));
	toast.addEventListener("mouseleave", () => {
		timeout = setTimeout(() => removeToast(toast), DURATION);
	});

	// Manual close
	toast.querySelector(".toast-close").addEventListener("click", () => {
		clearTimeout(timeout);
		removeToast(toast);
	});
}

function removeToast(toast) {
	toast.classList.add("translate-x-10", "opacity-0");
	setTimeout(() => toast.remove(), 300);
}

document.addEventListener("DOMContentLoaded", () => {
	eventBus.on("notify:success", (msg) => showToast(msg, "success"));
	eventBus.on("notify:error", (msg) => showToast(msg, "error"));
});
