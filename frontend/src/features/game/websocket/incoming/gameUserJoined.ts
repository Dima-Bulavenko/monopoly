import z from "zod";
import { useGameStore } from "#/stores/game.store";
import { PlayerSchema } from "../../api/gameStateSchema";

const UserJoinedPayloadSchema = z.object({
	game_id: z.string(),
	player: PlayerSchema,
});

export const GameUserJoined = z.object({
	type: z.literal("joined_game"),
	payload: UserJoinedPayloadSchema,
});

export type GameUserJoined = z.infer<typeof GameUserJoined>;

export function handleGameUserJoined(message: z.infer<typeof GameUserJoined>) {
	useGameStore.getState().updateActiveGame((gameState) => {
		gameState.players.push(message.payload.player);
	});
}
