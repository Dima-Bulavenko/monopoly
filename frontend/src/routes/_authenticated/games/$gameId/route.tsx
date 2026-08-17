import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Skeleton } from "#/components/ui/skeleton";
import { GameSchema } from "#/features/game/api/gameStateSchema";
import {
	gameStateOptions,
	getBoardOptions,
} from "#/features/game/api/queryOptions";
import { useGameStore } from "#/stores/game.store";

export const Route = createFileRoute("/_authenticated/games/$gameId")({
	loader: async ({ params: { gameId }, context: { queryClient } }) => {
		let game = useGameStore.getState().gameState;
		const [state] = await Promise.all([
			game?.game_id === gameId
				? Promise.resolve(null)
				: queryClient.fetchQuery(gameStateOptions(gameId)),
			queryClient.prefetchQuery(getBoardOptions()),
		]);
		if (state) {
			game = GameSchema.parse(state);
			useGameStore.setState({ gameState: game });
		}
	},
	component: RouteComponent,
	pendingComponent: BoardSkeleton,
});

function BoardSkeleton() {
	return (
		<div className="flex min-h-screen items-center justify-center p-4">
			<Skeleton className="aspect-square w-full max-h-screen" />
		</div>
	);
}

function RouteComponent() {
	return <Outlet />;
}
