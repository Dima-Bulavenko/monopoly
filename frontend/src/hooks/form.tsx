import { createFormHook } from "@tanstack/react-form";
import { lazy } from "react";
import { fieldContext, formContext } from "./form-context";

const TextField = lazy(() => import("#/components/form/TextField"));
const EmailField = lazy(() => import("#/components/form/EmailField"));
const PasswordField = lazy(() => import("#/components/form/PasswordField"));
const SubmitButton = lazy(() => import("#/components/form/SubmitButton"));
const PlayersNumberField = lazy(
	() => import("#/features/game/ui/PlayersNumberField"),
);

export const { useAppForm, withFieldGroup, withForm } = createFormHook({
	fieldContext,
	formContext,
	fieldComponents: {
		TextField,
		PasswordField,
		EmailField,
		PlayersNumberField,
	},
	formComponents: {
		SubmitButton,
	},
});
