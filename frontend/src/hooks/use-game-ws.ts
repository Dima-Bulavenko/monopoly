import { useCallback, useEffect, useRef, useState } from "react";
import { WsClient } from "#/lib/ws-client";
import { useAuthStore } from "#/stores/auth.store";
import { useGameStore } from "#/stores/game.store";
import type { InboundMessage, OutboundMessage } from "#/types/ws";

export function useGameWebSocket(gameId: string) {
	const accessToken = useAuthStore((s) => s.accessToken);
	const setGameState = useGameStore((s) => s.setGameState);
	const appendEvents = useGameStore((s) => s.appendEvents);
	const setWsError = useGameStore((s) => s.setWsError);
	const reset = useGameStore((s) => s.reset);

	const clientRef = useRef<WsClient | null>(null);
	const [isConnected, setIsConnected] = useState(false);

	useEffect(() => {
		if (!accessToken) return;

		const client = new WsClient();
		clientRef.current = client;

		const handler = (msg: OutboundMessage) => {
			if (msg.type === "game_update") {
				setGameState(msg.state);
				appendEvents(msg.events);
				setIsConnected(true);
			} else if (msg.type === "error") {
				setWsError(msg.message);
			}
		};

		client.addHandler(handler);
		client.connect(gameId, accessToken);

		// Poll isConnected state since WebSocket doesn't emit React events
		const interval = setInterval(() => {
			setIsConnected(client.isConnected);
		}, 500);

		return () => {
			clearInterval(interval);
			client.removeHandler(handler);
			client.disconnect();
			reset();
		};
	}, [gameId, accessToken, setGameState, appendEvents, setWsError, reset]);

	const sendAction = useCallback((msg: InboundMessage) => {
		clientRef.current?.send(msg);
	}, []);

	return { sendAction, isConnected };
}
