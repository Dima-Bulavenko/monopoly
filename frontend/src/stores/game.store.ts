import { create } from "zustand";
import type { GameStateType } from "#/features/game/api/gameStateSchema";
import type { OutboundMessage } from "#/types/ws";

type GameState = GameStateType;
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

export function useActiveGame<T>(selector: (state: GameState) => T): T {
	return useGameStore((store) => {
		if (!store.gameState) {
			throw new Error(
				"useActiveGame was called outside of a loaded game route.",
			);
		}
		return selector(store.gameState);
	});
}
