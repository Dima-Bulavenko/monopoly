import { createFileRoute } from "@tanstack/react-router";
import { LobbyPage } from "#/features/game/ui/LobbyPage";

export const Route = createFileRoute("/_authenticated/games/$gameId/lobby")({
	component: LobbyPage,
});
