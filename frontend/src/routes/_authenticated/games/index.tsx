import { useForm } from "@tanstack/react-form";
import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useState } from "react";
import { Button } from "#/components/ui/button";
import { Label } from "#/components/ui/label";
import { Slider } from "#/components/ui/slider";
import { useCreateGame } from "#/hooks/use-game";

export const Route = createFileRoute("/_authenticated/games/")({
	component: GamesPage,
});

function GamesPage() {
	const createGame = useCreateGame();
	const router = useRouter();
	const [serverError, setServerError] = useState<string | null>(null);

	const form = useForm({
		defaultValues: { max_players: 3 },
		onSubmit: async ({ value }) => {
			setServerError(null);
			try {
				const game = await createGame.mutateAsync(value);
				await router.navigate({
					to: "/games/$gameId",
					params: { gameId: game.game_id },
				});
			} catch (err: unknown) {
				const msg =
					err instanceof Error ? err.message : "Failed to create game.";
				setServerError(msg);
			}
		},
	});

	return (
		<div className="mx-auto max-w-md px-4 py-12">
			<h1 className="mb-8 text-3xl font-bold text-gray-900">New Game</h1>

			{serverError && (
				<p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
					{serverError}
				</p>
			)}

			<form
				onSubmit={(e) => {
					e.preventDefault();
					form.handleSubmit();
				}}
				className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
			>
				<form.Field name="max_players">
					{(field) => (
						<div className="space-y-3">
							<div className="flex items-center justify-between">
								<Label>Max players</Label>
								<span className="text-lg font-semibold text-gray-900">
									{field.state.value}
								</span>
							</div>
							<Slider
								min={2}
								max={6}
								step={1}
								value={[field.state.value]}
								onValueChange={([v]) => field.handleChange(v)}
								className="py-1"
							/>
							<div className="flex justify-between text-xs text-gray-400">
								<span>2</span>
								<span>6</span>
							</div>
						</div>
					)}
				</form.Field>

				<form.Subscribe selector={(s) => s.isSubmitting}>
					{(isSubmitting) => (
						<Button
							type="submit"
							className="mt-6 w-full"
							disabled={isSubmitting}
						>
							{isSubmitting ? "Creating…" : "Create Game"}
						</Button>
					)}
				</form.Subscribe>
			</form>
		</div>
	);
}
