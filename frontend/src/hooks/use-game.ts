import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "#/lib/api";
import type {
	CreateGameRequest,
	GameResponse,
	GameStateResponse,
} from "#/types/api";

export function useCreateGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (data: CreateGameRequest) =>
			api.post<GameResponse>("/games/", data).then((r) => r.data),
		onSuccess: () => qc.invalidateQueries({ queryKey: ["games"] }),
	});
}

export function useJoinGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (gameId: string) =>
			api.post<GameResponse>(`/games/${gameId}/join`).then((r) => r.data),
		onSuccess: (_data, gameId) =>
			qc.invalidateQueries({ queryKey: ["game", gameId] }),
	});
}

export function useStartGame() {
	const qc = useQueryClient();
	return useMutation({
		mutationFn: (gameId: string) =>
			api.post<GameResponse>(`/games/${gameId}/start`).then((r) => r.data),
		onSuccess: (_data, gameId) =>
			qc.invalidateQueries({ queryKey: ["game", gameId] }),
	});
}

export function useGameState(gameId: string, enabled = true) {
	return useQuery({
		queryKey: ["game", gameId],
		queryFn: () =>
			api.get<GameStateResponse>(`/games/${gameId}/state`).then((r) => r.data),
		enabled,
		refetchInterval: 3000,
	});
}
