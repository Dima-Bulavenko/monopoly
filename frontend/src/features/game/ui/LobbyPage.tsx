import { useActiveGame } from "#/stores/game.store";
import { GamePlayer } from "./GamePlayer";

export function LobbyPage() {
	const players = useActiveGame((state) => state.players);
	const amountOfPlayers = useActiveGame((state) => state.players.length);
	const maxPlayers = useActiveGame((state) => state.max_players);
	return (
		<div>
			<div>{`Players: ${amountOfPlayers} / ${maxPlayers}`}</div>
			{players.map((player) => (
				<GamePlayer key={player.player_id} playerName={player.name} />
			))}
		</div>
	);
}
