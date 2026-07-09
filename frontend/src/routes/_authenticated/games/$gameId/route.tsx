import { createFileRoute, Outlet } from "@tanstack/react-router";
import { GameSchema } from "#/features/game/api/gameStateSchema";
import { gameStateOptions } from "#/features/game/api/queryOptions";
import { useGameStore } from "#/stores/game.store";

export const Route = createFileRoute("/_authenticated/games/$gameId")({
	loader: async ({ params: { gameId }, context: { queryClient } }) => {
		const state = await queryClient.fetchQuery(gameStateOptions(gameId));
		useGameStore.setState({ gameState: GameSchema.parse(state) });
	},
	component: RouteComponent,
});

function RouteComponent() {
	return <Outlet />;
}
