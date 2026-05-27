import { mutationOptions, queryOptions } from "@tanstack/react-query";
import {
	createGame,
	getGameState,
	joinGame,
	startGame,
} from "#/client/sdk.gen";
import type { CreateGameRequest } from "#/client/types.gen";

export const gameKeys = {
	all: ["game"] as const,
	create: () => [...gameKeys.all, "create"] as const,
	join: () => [...gameKeys.all, "join"] as const,
	start: () => [...gameKeys.all, "start"] as const,
	state: (gameId: string) => [...gameKeys.all, gameId, "state"] as const,
} as const;

export function createGameOptions() {
	return mutationOptions({
		mutationKey: gameKeys.create(),
		mutationFn: (body: CreateGameRequest) =>
			createGame({ body, throwOnError: true }).then((res) => res.data),
	});
}

export function joinGameOptions() {
	return mutationOptions({
		mutationKey: gameKeys.join(),
		mutationFn: (gameId: string) =>
			joinGame({ path: { game_id: gameId }, throwOnError: true }).then(
				(res) => res.data,
			),
	});
}

export function startGameOptions() {
	return mutationOptions({
		mutationKey: gameKeys.start(),
		mutationFn: (gameId: string) =>
			startGame({ path: { game_id: gameId }, throwOnError: true }),
	});
}

export function gameStateOptions(gameId: string) {
	return queryOptions({
		queryKey: gameKeys.state(gameId),
		queryFn: () =>
			getGameState({ path: { game_id: gameId }, throwOnError: true }).then(
				(res) => res.data,
			),
	});
}
