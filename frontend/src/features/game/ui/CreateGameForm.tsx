import { Button } from "#/components/ui/button";
import { useAppForm } from "#/hooks/form";

export function CreateGameForm() {
	const form = useAppForm({
		defaultValues: { max_players: 3 },
		onSubmit: async ({ value }) => {
			console.log(value);
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
			<form.AppField name="max_players">
				{(field) => <field.PlayersNumberField />}
			</form.AppField>

			<form.Subscribe selector={(s) => s.isSubmitting}>
				{(isSubmitting) => (
					<Button type="submit" className="mt-6 w-full" disabled={isSubmitting}>
						{isSubmitting ? "Creating…" : "Create Game"}
					</Button>
				)}
			</form.Subscribe>
		</form>
	);
}
