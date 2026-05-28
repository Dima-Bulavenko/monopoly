import { createFileRoute } from "@tanstack/react-router";
import { CreateGameForm } from "#/features/game/ui/CreateGameForm";

export const Route = createFileRoute("/_authenticated/games/")({
	component: GamesPage,
});

function GamesPage() {
	return (
		<div className="mx-auto max-w-md px-4 py-12">
			<h1 className="mb-8 text-3xl font-bold text-gray-900">New Game</h1>
			<CreateGameForm />
		</div>
	);
}
