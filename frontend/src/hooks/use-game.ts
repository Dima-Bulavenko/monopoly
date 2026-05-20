import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	createGame,
	getGameState,
	joinGame,
	startGame,
} from "#/client/sdk.gen";
import type { CreateGameRequest } from "#/client/types.gen";

export function useCreateGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (data: CreateGameRequest) =>
			createGame({ body: data, throwOnError: true }).then((r) => r.data),
		onSuccess: () => qc.invalidateQueries({ queryKey: ["games"] }),
	});
}

export function useJoinGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (gameId: string) =>
			joinGame({ path: { game_id: gameId }, throwOnError: true }).then(
				(r) => r.data,
			),
		onSuccess: (_data, gameId) =>
			qc.invalidateQueries({ queryKey: ["game", gameId] }),
	});
}

export function useStartGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (gameId: string) =>
			startGame({ path: { game_id: gameId }, throwOnError: true }).then(
				(r) => r.data,
			),
		onSuccess: (_data, gameId) =>
			qc.invalidateQueries({ queryKey: ["game", gameId] }),
	});
}

export function useGameState(gameId: string, enabled = true) {
	return useQuery({
		queryKey: ["game", gameId],
		queryFn: () =>
			getGameState({ path: { game_id: gameId }, throwOnError: true }).then(
				(r) => r.data,
			),
		enabled,
		refetchInterval: 3000,
	});
}
