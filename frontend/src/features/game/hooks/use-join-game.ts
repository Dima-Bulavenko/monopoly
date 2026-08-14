import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { joinGameOptions } from "#/features/game/api/queryOptions";
import { useGameStore } from "#/stores/game.store";
import { GameSchema } from "../api/gameStateSchema";

export function useJoinGame() {
	const router = useRouter();

	return useMutation({
		...joinGameOptions(),
		onSuccess: (data) => {
			useGameStore.setState({ gameState: GameSchema.parse(data) });
			router.navigate({
				to: "/games/$gameId/lobby",
				params: { gameId: data.game_id },
			});
		},
	});
}
