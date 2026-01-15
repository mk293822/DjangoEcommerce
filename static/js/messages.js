import eventBus from "./event_bus.js";

document.addEventListener("DOMContentLoaded", () => {
	const messages = JSON.parse(
		document.getElementById("js_messages_data").textContent || "[]"
	);

	messages.forEach((msg) => {
		let eventName;
		switch (msg.tags) {
			case "success":
				eventName = "notify:success";
				break;
			case "error":
				eventName = "notify:error";
				break;
			case "info":
				eventName = "notify:info";
				break;
			default:
				eventName = "notify:info";
		}

		// Emit via your event bus
		eventBus.emit(eventName, msg.text);
	});
});
