import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated/games/$gameId")({
	component: GameRoom,
});

function GameRoom() {
	return <div>Game Room</div>;
}
