import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { createGameOptions } from "#/features/game/api/queryOptions";

export function useCreateGame() {
	const router = useRouter();

	return useMutation({
		...createGameOptions(),
		onSuccess: (data) => {
			router.navigate({
				to: "/games/$gameId",
				params: { gameId: data.game_id },
			});
		},
	});
}
