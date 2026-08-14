import { createFileRoute, Outlet } from "@tanstack/react-router";
import { GameSchema } from "#/features/game/api/gameStateSchema";
import { gameStateOptions } from "#/features/game/api/queryOptions";
import { useGameStore } from "#/stores/game.store";

export const Route = createFileRoute("/_authenticated/games/$gameId")({
	loader: async ({ params: { gameId }, context: { queryClient } }) => {
		let game = useGameStore.getState().gameState;
		if (game?.game_id === gameId) return;
		const state = await queryClient.fetchQuery(gameStateOptions(gameId));
		game = GameSchema.parse(state);
		useGameStore.setState({ gameState: game });
	},
	component: RouteComponent,
});

function RouteComponent() {
	return <Outlet />;
}
