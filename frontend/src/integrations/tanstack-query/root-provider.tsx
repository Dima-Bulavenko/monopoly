import { QueryClient } from "@tanstack/react-query";
import { WsClient } from "#/lib/ws-client";

export function getContext() {
	const queryClient = new QueryClient();
	const wsClient = new WsClient();

	return {
		queryClient,
		wsClient,
	};
}
export default function TanstackQueryProvider() {}
