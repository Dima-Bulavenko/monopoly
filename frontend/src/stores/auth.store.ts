import { create } from "zustand";
import { persist } from "zustand/middleware";
import { decodeJwtPayload } from "#/lib/jwt";

interface AuthState {
	accessToken: string | null;
	userId: string | null;
	displayName: string | null;
	setAuth: (accessToken: string) => void;
	clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
	persist(
		(set) => ({
			accessToken: null,
			userId: null,
			displayName: null,

			setAuth(accessToken: string) {
				try {
					const payload = decodeJwtPayload(accessToken);
					set({
						accessToken,
						userId: payload.sub,
						displayName: payload.display_name ?? null,
					});
				} catch {
					set({ accessToken, userId: null, displayName: null });
				}
			},

			clearAuth() {
				set({ accessToken: null, userId: null, displayName: null });
			},
		}),
		{
			name: "monopoly-auth",
			partialize: (state) => ({
				accessToken: state.accessToken,
				userId: state.userId,
				displayName: state.displayName,
			}),
		},
	),
);
