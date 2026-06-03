import { useMutation } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import { joinGameOptions } from "#/features/game/api/queryOptions";

export function useJoinGame() {
	const router = useRouter();

	return useMutation({
		...joinGameOptions(),
		onSuccess: (data) => {
			router.navigate({
				to: "/games/$gameId",
				params: { gameId: data.game_id },
			});
		},
	});
}
