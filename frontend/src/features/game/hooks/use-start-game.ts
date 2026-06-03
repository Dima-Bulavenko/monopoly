import { useMutation } from "@tanstack/react-query";
import { startGameOptions } from "#/features/game/api/queryOptions";

export function useStartGame() {
	return useMutation({
		...startGameOptions(),
	});
}
