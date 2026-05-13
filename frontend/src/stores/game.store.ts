import { create } from "zustand";
import type { OutboundMessage } from "#/types/ws";

type GameState = Extract<OutboundMessage, { type: "game_update" }>["state"];
type ServerEvent = Extract<
	OutboundMessage,
	{ type: "game_update" }
>["events"][number];

const MAX_EVENTS = 200;

interface GameStoreState {
	gameState: GameState | null;
	events: ServerEvent[];
	wsError: string | null;
	setGameState: (state: GameState) => void;
	appendEvents: (events: ServerEvent[]) => void;
	setWsError: (error: string | null) => void;
	reset: () => void;
}

export const useGameStore = create<GameStoreState>()((set) => ({
	gameState: null,
	events: [],
	wsError: null,

	setGameState(gameState) {
		set({ gameState });
	},

	appendEvents(newEvents) {
		set((s) => ({
			events: [...s.events, ...newEvents].slice(-MAX_EVENTS),
		}));
	},

	setWsError(wsError) {
		set({ wsError });
	},

	reset() {
		set({ gameState: null, events: [], wsError: null });
	},
}));
