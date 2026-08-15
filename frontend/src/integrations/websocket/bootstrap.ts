import {
	GameStarted,
	handleGameStarted,
} from "#/features/game/websocket/incoming/gameStarted";
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
	wsDispatcher.register(GameStarted, handleGameStarted);

	wsClient.onMessage((message) => {
		wsDispatcher.dispatch(message);
	});
	return {
		wsClient,
		wsDispatcher,
	};
}
