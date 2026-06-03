import { FieldGroup } from "#/components/ui/field";
import { useCreateGame } from "#/features/game/hooks";
import { useAppForm } from "#/hooks/form";

export function CreateGameForm() {
	const { mutateAsync: createGame } = useCreateGame();

	const form = useAppForm({
		defaultValues: { max_players: 3 },
		onSubmit: async ({ value }) => {
			await createGame(value);
		},
	});

	return (
		<form
			onSubmit={(e) => {
				e.preventDefault();
				form.handleSubmit();
			}}
			className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
		>
			<FieldGroup>
				<form.AppField name="max_players">
					{(field) => <field.PlayersNumberField />}
				</form.AppField>

				<form.AppForm>
					<form.SubmitButton label="Create Game" />
				</form.AppForm>
			</FieldGroup>
		</form>
	);
}
