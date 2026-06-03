import { useQuery } from "@tanstack/react-query";
import { gameStateOptions } from "#/features/game/api/queryOptions";

export function useGameState(gameId: string) {
	return useQuery(gameStateOptions(gameId));
}
