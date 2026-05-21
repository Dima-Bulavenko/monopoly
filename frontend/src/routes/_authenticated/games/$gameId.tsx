import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ActionPanel } from "#/components/game/action-panel/action-panel";
import { Board } from "#/components/game/board/board";
import { EventLog } from "#/components/game/event-log";
import { PlayerPanel } from "#/components/game/player-panel";
import { Button } from "#/components/ui/button";
import { useGameState, useJoinGame, useStartGame } from "#/hooks/use-game";
import { useGameWebSocket } from "#/hooks/use-game-ws";
import { useAuthStore } from "#/stores/auth.store";
import { useGameStore } from "#/stores/game.store";
import type { GameStatePlayer, GameStateProperty } from "#/types/api";

export const Route = createFileRoute("/_authenticated/games/$gameId")({
	component: GameRoom,
});

function GameRoom() {
	const { gameId } = Route.useParams();
	const userId = useAuthStore((s) => s.userId);

	// HTTP game state for lobby (before WS connected)
	const { data: httpState, refetch: refetchState } = useGameState(gameId);

	// WebSocket — connects immediately (server may reject if not joined yet, that's fine)
	const { sendAction, isConnected } = useGameWebSocket(gameId);

	// WS game state (authoritative once connected and in progress)
	const wsGameState = useGameStore((s) => s.gameState);
	const wsError = useGameStore((s) => s.wsError);

	const joinGame = useJoinGame();
	const startGame = useStartGame();
	const [actionError, setActionError] = useState<string | null>(null);

	// Use WS state if available and in-progress, fall back to HTTP state for lobby
	const gameStatus = wsGameState?.status ?? httpState?.status;
	const isInProgress = gameStatus === "in_progress";
	const isFinished = gameStatus === "finished";

	async function handleJoin() {
		setActionError(null);
		try {
			await joinGame.mutateAsync(gameId);
			await refetchState();
		} catch (err: unknown) {
			setActionError(err instanceof Error ? err.message : "Failed to join.");
		}
	}

	async function handleStart() {
		setActionError(null);
		try {
			await startGame.mutateAsync(gameId);
			await refetchState();
		} catch (err: unknown) {
			setActionError(err instanceof Error ? err.message : "Failed to start.");
		}
	}

	// ---- LOBBY VIEW ----
	if (!isInProgress && !isFinished) {
		const players = httpState?.players ?? [];
		const isJoined = players.some(
			(p) => (p as { player_id: string }).player_id === userId,
		);
		const canStart = isJoined && players.length >= 2;

		return (
			<div className="mx-auto max-w-md px-4 py-12">
				<h1 className="mb-2 text-2xl font-bold text-gray-900">Game Lobby</h1>
				<p className="mb-1 text-sm text-gray-500">
					Game ID:{" "}
					<code className="rounded bg-gray-100 px-1 font-mono text-xs">
						{gameId}
					</code>
				</p>
				<p className="mb-6 text-sm text-gray-500">
					Share this ID so others can join!
				</p>

				{actionError && (
					<p className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">
						{actionError}
					</p>
				)}

				<div className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm">
					<div className="mb-4">
						<h2 className="mb-2 text-sm font-semibold text-gray-500 uppercase tracking-wider">
							Players ({players.length} / {httpState?.max_players ?? "?"})
						</h2>
						{players.length === 0 ? (
							<p className="text-sm text-gray-400 italic">No players yet…</p>
						) : (
							<ul className="space-y-1">
								{players.map((p, i) => {
									const player = p as { player_id: string; name: string };
									return (
										<li
											key={player.player_id ?? i}
											className="text-sm text-gray-700"
										>
											{player.name}
											{player.player_id === userId && (
												<span className="ml-1 text-xs text-blue-500">
													(you)
												</span>
											)}
										</li>
									);
								})}
							</ul>
						)}
					</div>

					<div className="flex flex-col gap-2">
						{!isJoined && (
							<Button onClick={handleJoin} disabled={joinGame.isPending}>
								{joinGame.isPending ? "Joining…" : "Join Game"}
							</Button>
						)}
						{canStart && (
							<Button onClick={handleStart} disabled={startGame.isPending}>
								{startGame.isPending ? "Starting…" : "Start Game"}
							</Button>
						)}
						{isJoined && !canStart && (
							<p className="text-sm text-gray-400 italic">
								Waiting for more players…
							</p>
						)}
					</div>
				</div>

				<div className="mt-4">
					<Link to="/games" className="text-sm text-blue-600 hover:underline">
						← Back to Games
					</Link>
				</div>
			</div>
		);
	}

	// ---- FINISHED VIEW ----
	if (isFinished) {
		const winner = wsGameState?.players.find(
			(p: GameStatePlayer) => !p.is_bankrupt,
		);
		return (
			<div className="flex min-h-[80vh] flex-col items-center justify-center gap-4 text-center">
				<h1 className="text-4xl font-bold text-gray-900">🏆 Game Over!</h1>
				{winner && (
					<p className="text-xl text-gray-700">
						Winner: <span className="font-bold">{winner.name}</span>
					</p>
				)}
				<Link
					to="/games"
					className="mt-4 rounded-lg bg-blue-600 px-5 py-2.5 text-white font-medium hover:bg-blue-700"
				>
					New Game
				</Link>
			</div>
		);
	}

	// ---- IN-PROGRESS VIEW ----
	if (!wsGameState) {
		return (
			<div className="flex min-h-[60vh] items-center justify-center">
				<p className="text-gray-500">
					{isConnected ? "Loading game state…" : "Connecting to game…"}
				</p>
			</div>
		);
	}

	const playerPositions: Record<string, number> = {};
	const playerNames: Record<string, string> = {};
	for (const p of wsGameState.players) {
		playerPositions[p.player_id] = p.position;
		playerNames[p.player_id] = p.name;
	}

	const currentPlayer = wsGameState.players[wsGameState.current_player_index];
	const currentPlayerName = currentPlayer?.name ?? null;

	// Normalize properties to include square_index from key
	const normalizedProperties = Object.fromEntries(
		Object.entries(
			wsGameState.properties as Record<string, GameStateProperty>,
		).map(([key, val]) => [
			key,
			{ ...val, square_index: val.square_index ?? Number(key) },
		]),
	);

	return (
		<div className="flex h-[calc(100vh-57px)] flex-col overflow-hidden">
			{/* Connection/error banner */}
			{!isConnected && (
				<div className="bg-yellow-100 px-4 py-1 text-center text-xs text-yellow-800">
					Reconnecting to game…
				</div>
			)}
			{wsError && (
				<div className="bg-red-100 px-4 py-1 text-center text-xs text-red-700">
					{wsError}
				</div>
			)}

			<div className="flex flex-1 gap-3 overflow-hidden p-3">
				{/* Left sidebar — player list */}
				<aside className="w-52 shrink-0 overflow-y-auto">
					<PlayerPanel
						players={wsGameState.players}
						currentPlayerIndex={wsGameState.current_player_index}
						properties={normalizedProperties}
						userId={userId}
					/>
				</aside>

				{/* Center — board */}
				<main className="flex flex-1 flex-col items-center justify-start gap-3 overflow-y-auto">
					<Board
						playerPositions={playerPositions}
						playerNames={playerNames}
						properties={normalizedProperties}
						freeParkingPot={wsGameState.free_parking_pot}
						lastRoll={wsGameState.last_roll}
						phase={wsGameState.phase}
						currentPlayerName={currentPlayerName}
					/>
					<div className="w-full" style={{ maxWidth: "min(90vw, 680px)" }}>
						<EventLog />
					</div>
				</main>

				{/* Right sidebar — actions */}
				<aside className="w-64 shrink-0 overflow-y-auto">
					<ActionPanel
						phase={wsGameState.phase}
						userId={userId}
						currentPlayerIndex={wsGameState.current_player_index}
						players={wsGameState.players}
						properties={normalizedProperties}
						pendingAuction={wsGameState.pending_auction}
						pendingTrade={wsGameState.pending_trade}
						sendAction={sendAction}
					/>
				</aside>
			</div>
		</div>
	);
}
