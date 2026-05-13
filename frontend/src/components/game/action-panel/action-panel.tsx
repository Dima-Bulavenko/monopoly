import { Button } from "#/components/ui/button";
import type { InboundMessage } from "#/types/ws";
import { AuctionPanel } from "./auction-panel";
import { BuyDecisionPanel } from "./buy-decision-panel";
import { EndOfTurnPanel } from "./end-of-turn-panel";
import { JailPanel } from "./jail-panel";
import { RollDicePanel } from "./roll-dice-panel";

interface PropertyState {
	owner_id: string | null;
	houses: number;
	hotel: boolean;
	mortgaged: boolean;
	square_index: number;
}

interface Player {
	player_id: string;
	name: string;
	balance: number;
	position: number;
	in_jail: boolean;
	jail_turns: number;
	get_out_of_jail_cards: number;
	is_bankrupt: boolean;
}

interface PendingAuction {
	property_index: number;
	bids: Record<string, number>;
	current_bidder_index: number;
	passed_player_ids: string[];
}

interface PendingTrade {
	trade_id: string;
	proposer_id: string;
	target_id: string;
	offer_money: number;
	offer_property_indices: number[];
	request_money: number;
	request_property_indices: number[];
	status: string;
}

interface ActionPanelProps {
	phase: string;
	userId: string | null;
	currentPlayerIndex: number;
	players: Player[];
	properties: Record<string, PropertyState>;
	pendingAuction: PendingAuction | null;
	pendingTrade: PendingTrade | null;
	sendAction: (msg: InboundMessage) => void;
}

export function ActionPanel({
	phase,
	userId,
	currentPlayerIndex,
	players,
	properties,
	pendingAuction,
	pendingTrade,
	sendAction,
}: ActionPanelProps) {
	const currentPlayer = players[currentPlayerIndex];
	const isMyTurn = currentPlayer?.player_id === userId;
	const myPlayer = players.find((p) => p.player_id === userId);

	// Trade response for the user who is the target
	const pendingTradeForMe =
		pendingTrade &&
		pendingTrade.status === "pending" &&
		pendingTrade.target_id === userId;

	return (
		<div className="flex flex-col gap-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
			<h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
				Actions
			</h2>

			{/* Pending trade incoming */}
			{pendingTradeForMe && pendingTrade && (
				<div className="rounded-md border border-yellow-300 bg-yellow-50 p-3">
					<p className="text-sm font-semibold text-yellow-800 mb-2">
						🤝 Trade Offer from{" "}
						{players.find((p) => p.player_id === pendingTrade.proposer_id)
							?.name ?? "player"}
					</p>
					<p className="text-xs text-yellow-700 mb-3">
						They offer: ${pendingTrade.offer_money}
						{pendingTrade.offer_property_indices.length > 0
							? ` + ${pendingTrade.offer_property_indices.length} propert${pendingTrade.offer_property_indices.length === 1 ? "y" : "ies"}`
							: ""}
						{" · "}They request: ${pendingTrade.request_money}
						{pendingTrade.request_property_indices.length > 0
							? ` + ${pendingTrade.request_property_indices.length} propert${pendingTrade.request_property_indices.length === 1 ? "y" : "ies"}`
							: ""}
					</p>
					<div className="flex gap-2">
						<Button
							size="sm"
							onClick={() =>
								sendAction({
									action: "accept_trade",
									trade_id: pendingTrade.trade_id,
								})
							}
						>
							✅ Accept
						</Button>
						<Button
							size="sm"
							variant="outline"
							onClick={() =>
								sendAction({
									action: "reject_trade",
									trade_id: pendingTrade.trade_id,
								})
							}
						>
							❌ Reject
						</Button>
					</div>
				</div>
			)}

			{/* Auction phase — any active player can bid */}
			{phase === "in_auction" && pendingAuction ? (
				<AuctionPanel
					auction={pendingAuction}
					players={players}
					userId={userId}
					sendAction={sendAction}
				/>
			) : !isMyTurn ? (
				<p className="text-sm text-gray-500 italic">
					Waiting for {currentPlayer?.name ?? "player"}'s turn…
				</p>
			) : myPlayer?.is_bankrupt ? (
				<p className="text-sm text-red-500">You are bankrupt.</p>
			) : phase === "waiting_for_roll" ? (
				myPlayer?.in_jail ? (
					<JailPanel
						jailTurns={myPlayer.jail_turns}
						getOutOfJailCards={myPlayer.get_out_of_jail_cards}
						sendAction={sendAction}
					/>
				) : (
					<RollDicePanel sendAction={sendAction} />
				)
			) : phase === "waiting_for_buy_decision" ? (
				<BuyDecisionPanel
					squareIndex={myPlayer?.position ?? 0}
					sendAction={sendAction}
				/>
			) : phase === "in_jail" ? (
				<JailPanel
					jailTurns={myPlayer?.jail_turns ?? 0}
					getOutOfJailCards={myPlayer?.get_out_of_jail_cards ?? 0}
					sendAction={sendAction}
				/>
			) : phase === "end_of_turn" || phase === "waiting_for_trade_response" ? (
				<EndOfTurnPanel
					userId={userId}
					properties={properties}
					players={players}
					sendAction={sendAction}
				/>
			) : (
				<p className="text-sm text-gray-500">Phase: {phase}</p>
			)}
		</div>
	);
}
