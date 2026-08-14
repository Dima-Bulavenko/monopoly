import { mutationOptions, queryOptions } from "@tanstack/react-query";
import { createGame, getGame, joinGame } from "#/client/sdk.gen";
import type { CreateGameDto } from "#/client/types.gen";

export const gameKeys = {
	all: ["game"] as const,
	create: () => [...gameKeys.all, "create"] as const,
	join: () => [...gameKeys.all, "join"] as const,
	state: (gameId: string) => [...gameKeys.all, gameId, "state"] as const,
} as const;

export function createGameOptions() {
	return mutationOptions({
		mutationKey: gameKeys.create(),
		mutationFn: (body: CreateGameDto) =>
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

export function gameStateOptions(gameId: string) {
	return queryOptions({
		queryKey: gameKeys.state(gameId),
		queryFn: () =>
			getGame({ path: { game_id: gameId }, throwOnError: true }).then(
				(res) => res.data,
			),
	});
}
