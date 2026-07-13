import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type { GameStateType } from "#/features/game/api/gameStateSchema";

type GameState = GameStateType;

interface GameStoreState {
	gameState: GameState | null;
	setGameState: (state: GameState) => void;
	updateActiveGame: (recipe: (draft: GameState) => void) => void;
	reset: () => void;
}

export const useGameStore = create<GameStoreState>()(
	immer((set) => ({
		gameState: null,

		setGameState(gameState) {
			set({ gameState });
		},
		updateActiveGame(recipe) {
			set((state) => {
				if (!state.gameState) {
					console.warn("Attempted to update game state outside of a game.");
					return;
				}
				recipe(state.gameState);
			});
		},
		reset() {
			set({ gameState: null });
		},
	})),
);

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
