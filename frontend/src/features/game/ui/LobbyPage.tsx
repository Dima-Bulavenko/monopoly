import { getRouteApi } from "@tanstack/react-router";
import { useEffect } from "react";
import { useActiveGame } from "#/stores/game.store";
import { GamePlayer } from "./GamePlayer";

const route = getRouteApi("/_authenticated/games/$gameId/lobby");

function useLobby() {
	const players = useActiveGame((state) => state.players);
	const amountOfPlayers = useActiveGame((state) => state.players.length);
	const maxPlayers = useActiveGame((state) => state.max_players);
	const status = useActiveGame((state) => state.status);
	const navigate = route.useNavigate();
	const params = route.useParams();

	useEffect(() => {
		console.log("run useEffect");
		if (status === "in_progress") {
			navigate({ to: "/games/$gameId", params: { gameId: params.gameId } });
		}
	}, [status, params.gameId, navigate]);

	return { players, amountOfPlayers, maxPlayers, status };
}

export function LobbyPage() {
	const { players, amountOfPlayers, maxPlayers } = useLobby();
	return (
		<div>
			<div>{`Players: ${amountOfPlayers} / ${maxPlayers}`}</div>
			{players.map((player) => (
				<GamePlayer key={player.player_id} playerName={player.name} />
			))}
		</div>
	);
}
