import { Field, FieldLabel } from "#/components/ui/field";
import { ToggleGroup, ToggleGroupItem } from "#/components/ui/toggle-group";
import { useFieldContext } from "#/hooks/form-context";

const playerNumbers = [2, 3, 4, 5, 6];

export default function PlayersNumberField() {
	const field = useFieldContext<number>();
	return (
		<Field orientation="responsive">
			<FieldLabel>Number of Players</FieldLabel>
			<ToggleGroup
				type="single"
				value={String(field.state.value)}
				onValueChange={(value) => field.handleChange(Number(value))}
				onBlur={field.handleBlur}
				variant="outline"
			>
				{playerNumbers.map((num) => (
					<ToggleGroupItem key={num} value={String(num)}>
						{num}
					</ToggleGroupItem>
				))}
			</ToggleGroup>
		</Field>
	);
}
