import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { createGameOptions } from "#/features/game/api/queryOptions";
import { useGameStore } from "#/stores/game.store";
import { GameSchema } from "../api/gameStateSchema";

export function useCreateGame() {
	const router = useRouter();

	return useMutation({
		...createGameOptions(),
		onSuccess: (data) => {
			useGameStore.setState({ gameState: GameSchema.parse(data) });
			router.navigate({
				to: "/games/$gameId/lobby",
				params: { gameId: data.game_id },
			});
		},
	});
}
