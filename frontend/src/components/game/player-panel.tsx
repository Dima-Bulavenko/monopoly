import { cn } from "#/lib/utils";
import {
	BOARD_SQUARES,
	COLOR_GROUP_CLASSES,
	PLAYER_COLORS,
} from "./board/board-data";

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
	position: number;
	balance: number;
	in_jail: boolean;
	is_bankrupt: boolean;
	jail_turns: number;
	get_out_of_jail_cards: number;
}

interface PlayerPanelProps {
	players: Player[];
	currentPlayerIndex: number;
	properties: Record<string, PropertyState>;
	userId: string | null;
}

export function PlayerPanel({
	players,
	currentPlayerIndex,
	properties,
	userId,
}: PlayerPanelProps) {
	return (
		<div className="flex flex-col gap-2">
			<h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
				Players
			</h2>
			{players.map((player, idx) => {
				const isCurrent = idx === currentPlayerIndex;
				const isMe = player.player_id === userId;
				const posSquare = BOARD_SQUARES[player.position];
				const ownedProps = Object.values(properties).filter(
					(p) => p.owner_id === player.player_id,
				);

				return (
					<div
						key={player.player_id}
						className={cn(
							"rounded-lg border p-3 transition-all",
							isCurrent
								? "border-blue-400 bg-blue-50 shadow-sm"
								: "border-gray-200 bg-white",
							player.is_bankrupt && "opacity-50",
						)}
					>
						<div className="flex items-center gap-2">
							<div
								className={cn(
									"flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white",
									PLAYER_COLORS[idx % PLAYER_COLORS.length],
								)}
							>
								{player.name[0]?.toUpperCase()}
							</div>
							<div className="min-w-0 flex-1">
								<div className="flex items-baseline gap-1">
									<span className="truncate text-sm font-semibold text-gray-900">
										{player.name}
									</span>
									{isMe && (
										<span className="text-[0.6rem] text-blue-500 font-medium">
											(you)
										</span>
									)}
									{isCurrent && !player.is_bankrupt && (
										<span className="ml-auto text-[0.6rem] text-blue-600 font-semibold">
											▶ Turn
										</span>
									)}
									{player.is_bankrupt && (
										<span className="ml-auto text-[0.6rem] text-red-500 font-semibold">
											BANKRUPT
										</span>
									)}
								</div>
								<div className="text-xs text-gray-600">
									${player.balance.toLocaleString()}
								</div>
							</div>
						</div>

						<div className="mt-1.5 space-y-0.5 text-[0.65rem] text-gray-500">
							<div>📍 {posSquare?.name ?? `Square ${player.position}`}</div>
							{player.in_jail && (
								<div className="text-orange-600">
									⛓ In Jail ({player.jail_turns} turn
									{player.jail_turns !== 1 ? "s" : ""} left)
								</div>
							)}
							{player.get_out_of_jail_cards > 0 && (
								<div>🃏 {player.get_out_of_jail_cards}× Get Out of Jail</div>
							)}
						</div>

						{/* Property dots */}
						{ownedProps.length > 0 && (
							<div className="mt-2 flex flex-wrap gap-1">
								{ownedProps.map((prop) => {
									const sq = BOARD_SQUARES[prop.square_index];
									const colorClass = sq?.colorGroup
										? COLOR_GROUP_CLASSES[sq.colorGroup]
										: "bg-gray-400";
									return (
										<div
											key={prop.square_index}
											className={cn(
												"h-2.5 w-2.5 rounded-sm border border-black/10",
												colorClass,
												prop.mortgaged && "opacity-40",
											)}
											title={sq?.name ?? `Square ${prop.square_index}`}
										/>
									);
								})}
							</div>
						)}
					</div>
				);
			})}
		</div>
	);
}
