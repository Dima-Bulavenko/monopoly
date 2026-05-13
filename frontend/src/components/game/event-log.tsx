import { useEffect, useRef } from "react";
import { useGameStore } from "#/stores/game.store";
import type { OutboundMessage } from "#/types/ws";
import { BOARD_SQUARES } from "./board/board-data";

type ServerEvent = Extract<
	OutboundMessage,
	{ type: "game_update" }
>["events"][number];

function describeEvent(ev: ServerEvent): string {
	switch (ev.type) {
		case "DiceRolledEvent":
			return `🎲 Dice: ${ev.die1} + ${ev.die2} = ${ev.die1 + ev.die2}`;
		case "PlayerMovedEvent":
			return `🚶 Moved to ${BOARD_SQUARES[ev.to_position]?.name ?? ev.to_position}`;
		case "PassedGoEvent":
			return `✅ Passed GO! Collected $${ev.amount_collected}`;
		case "PropertyLandedEvent":
			return `🏠 Landed on ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index}`;
		case "RentPaidEvent":
			return `💸 Paid $${ev.amount} rent for ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index}`;
		case "PropertyBoughtEvent":
			return `🏦 Bought ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.price}`;
		case "PropertyMortgagedEvent":
			return `📋 Mortgaged ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.mortgage_value}`;
		case "PropertyUnmortgagedEvent":
			return `📋 Unmortgaged ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.cost}`;
		case "AuctionStartedEvent":
			return `🔨 Auction started for ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index}`;
		case "AuctionBidPlacedEvent":
			return `💰 Bid placed: $${ev.amount}`;
		case "AuctionPassedEvent":
			return `🚫 Passed auction`;
		case "AuctionWonEvent":
			return `🏆 Won ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.amount}`;
		case "AuctionEndedWithNoBidderEvent":
			return `🔨 Auction ended with no winner`;
		case "HouseBuiltEvent":
			return `🏘 Built house on ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.cost}`;
		case "HouseSoldEvent":
			return `🏘 Sold house on ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.refund}`;
		case "HotelBuiltEvent":
			return `🏨 Built hotel on ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.cost}`;
		case "HotelSoldEvent":
			return `🏨 Sold hotel on ${BOARD_SQUARES[ev.square_index]?.name ?? ev.square_index} for $${ev.refund}`;
		case "PlayerJailedEvent":
			return `⛓ Sent to Jail (${ev.reason.replace(/_/g, " ")})`;
		case "PlayerReleasedFromJailEvent":
			return `🔓 Released from Jail (${ev.method.replace(/_/g, " ")})`;
		case "TaxPaidEvent":
			return `🏛 Paid $${ev.amount} tax`;
		case "CardDrawnEvent":
			return `🃏 ${ev.deck === "chance" ? "Chance" : "Community Chest"}: ${ev.description}`;
		case "TradeProposedEvent":
			return `🤝 Trade proposed`;
		case "TradeAcceptedEvent":
			return `✅ Trade accepted`;
		case "TradeRejectedEvent":
			return `❌ Trade rejected`;
		case "BankruptcyDeclaredEvent":
			return `💀 Bankruptcy declared`;
		case "TurnEndedEvent":
			return `⏭ Turn ended`;
		case "GameStartedEvent":
			return `🎉 Game started!`;
		case "GameOverEvent":
			return `🏆 Game Over!`;
		default:
			return `Event: ${(ev as { type: string }).type}`;
	}
}

export function EventLog() {
	const events = useGameStore((s) => s.events);
	const bottomRef = useRef<HTMLDivElement>(null);

	// biome-ignore lint/correctness/useExhaustiveDependencies: scroll when events change
	useEffect(() => {
		bottomRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [events]);

	return (
		<div className="flex flex-col">
			<h2 className="mb-1 text-sm font-semibold text-gray-500 uppercase tracking-wider">
				Event Log
			</h2>
			<div className="h-36 overflow-y-auto rounded-lg border border-gray-200 bg-white p-2 text-xs">
				{events.length === 0 ? (
					<p className="text-gray-400 italic">No events yet…</p>
				) : (
					events.map((ev, i) => (
						// biome-ignore lint/suspicious/noArrayIndexKey: append-only log
						<div key={i} className="py-0.5 text-gray-700 leading-snug">
							{describeEvent(ev)}
						</div>
					))
				)}
				<div ref={bottomRef} />
			</div>
		</div>
	);
}
