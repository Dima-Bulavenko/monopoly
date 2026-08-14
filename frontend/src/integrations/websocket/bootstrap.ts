import {
	GameUserJoined,
	handleGameUserJoined,
} from "#/features/game/websocket/incoming/gameUserJoined";
import { Dispatcher } from "#/lib/websocket/dispatcher";
import { WebSocketClient } from "#/lib/websocket/ws-client";

export function bootstrapWebSocket() {
	const wsClient = new WebSocketClient("/ws");
	const wsDispatcher = new Dispatcher();
	wsDispatcher.register(GameUserJoined, handleGameUserJoined);

	wsClient.onMessage((message) => {
		wsDispatcher.dispatch(message);
	});
	return {
		wsClient,
		wsDispatcher,
	};
}
