import { createFileRoute } from "@tanstack/react-router";
import { FieldGroup } from "#/components/ui/field";
import { useJoinGame } from "#/features/game/hooks";
import { CreateGameForm } from "#/features/game/ui/CreateGameForm";
import { useAppForm } from "#/hooks/form";

export const Route = createFileRoute("/_authenticated/games/")({
	component: GamesPage,
});

function GamesPage() {
	return (
		<div className="mx-auto max-w-md px-4 py-12">
			<h1 className="mb-8 text-3xl font-bold text-gray-900">New Game</h1>
			<CreateGameForm />
			<JoinGameForm />
		</div>
	);
}

function JoinGameForm() {
	const { mutate: joinGame } = useJoinGame();

	const form = useAppForm({
		defaultValues: { game_id: "" },
		onSubmit: async ({ value }) => {
			await joinGame(value.game_id);
		},
	});

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				form.handleSubmit();
			}}
		>
			<FieldGroup>
				<form.AppField name="game_id">
					{(field) => <field.TextField id="game_id" label="Game ID" />}
				</form.AppField>
				<form.AppForm>
					<form.SubmitButton label="Join Game" />
				</form.AppForm>
			</FieldGroup>
		</form>
	);
}
