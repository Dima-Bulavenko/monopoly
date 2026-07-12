import { Dispatcher } from "#/lib/websocket/dispatcher";
import { WebSocketClient } from "#/lib/websocket/ws-client";

export function bootstrapWebSocket() {
	const wsClient = new WebSocketClient("/ws");
	const wsDispatcher = new Dispatcher();

	wsClient.onMessage((message) => {
		wsDispatcher.dispatch(message);
	});
	return {
		wsClient,
		wsDispatcher,
	};
}
