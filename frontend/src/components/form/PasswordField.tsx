import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";
import { useFieldContext } from "#/hooks/form-context";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import FormField from "./FormField";

type PasswordFieldProps = {
	label: string;
	id: string;
	placeholder?: string;
	description?: string;
};

export default function PasswordField({
	label,
	id,
	placeholder,
	description,
}: PasswordFieldProps) {
	const field = useFieldContext<string>();
	const [showPassword, setShowPassword] = useState(false);

	return (
		<FormField label={label} id={id} description={description}>
			<div className="relative">
				<Input
					id={id}
					type={showPassword ? "text" : "password"}
					placeholder={placeholder}
					value={field.state.value}
					onChange={(e) => field.handleChange(e.target.value)}
					onBlur={field.handleBlur}
				/>
				<Button
					className="absolute top-0 right-0 h-full px-3 hover:bg-transparent"
					onClick={() => setShowPassword(!showPassword)}
					size="icon"
					type="button"
					variant="ghost"
				>
					{showPassword ? (
						<EyeOff className="h-4 w-4 text-muted-foreground" />
					) : (
						<Eye className="h-4 w-4 text-muted-foreground" />
					)}
				</Button>
			</div>
		</FormField>
	);
}
