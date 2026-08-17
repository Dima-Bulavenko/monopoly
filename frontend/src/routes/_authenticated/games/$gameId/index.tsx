import { createFileRoute } from "@tanstack/react-router";
import { Board } from "#/features/game/ui/board/Board";

export const Route = createFileRoute("/_authenticated/games/$gameId/")({
	component: GameRoom,
});

function GameRoom() {
	return (
		<div className="flex min-h-screen items-center justify-center p-4">
			<Board />
		</div>
	);
}
