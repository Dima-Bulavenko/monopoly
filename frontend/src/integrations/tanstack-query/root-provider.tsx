import { QueryClient } from "@tanstack/react-query";
import { WebSocketClient } from "#/lib/websocket/ws-client";

export function getContext() {
	const queryClient = new QueryClient();
	const wsClient = new WebSocketClient("/ws");

	return {
		queryClient,
		wsClient,
	};
}
export default function TanstackQueryProvider() {}
