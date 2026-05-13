import { cn } from "#/lib/utils";
import type { BoardSquareData } from "./board-data";
import { COLOR_GROUP_CLASSES, PLAYER_COLORS } from "./board-data";

interface PropertyState {
	owner_id: string | null;
	houses: number;
	hotel: boolean;
	mortgaged: boolean;
}

interface PlayerToken {
	playerId: string;
	name: string;
	colorIndex: number;
}

interface BoardSquareProps {
	square: BoardSquareData;
	propertyState?: PropertyState;
	playerTokens: PlayerToken[];
	rotation?: 0 | 90 | 180 | 270;
	isCorner?: boolean;
}

export function BoardSquare({
	square,
	propertyState,
	playerTokens,
	rotation = 0,
	isCorner = false,
}: BoardSquareProps) {
	const colorClass = square.colorGroup
		? COLOR_GROUP_CLASSES[square.colorGroup]
		: null;

	const isMortgaged = propertyState?.mortgaged ?? false;

	return (
		<div
			className={cn(
				"relative flex flex-col overflow-hidden border border-gray-300 bg-white",
				isCorner ? "items-center justify-center" : "items-stretch",
				isMortgaged && "opacity-60",
			)}
			style={{ fontSize: "0.55rem" }}
		>
			{/* Color band — only on top for standard orientation, the parent rotates */}
			{colorClass && !isCorner && (
				<div className={cn("h-3 w-full shrink-0", colorClass)} />
			)}

			<div
				className="flex flex-1 flex-col items-center justify-between gap-0.5 p-0.5"
				style={{ transform: `rotate(${rotation}deg)` }}
			>
				{/* Square name */}
				<span
					className={cn(
						"text-center leading-tight font-semibold text-gray-800",
						isCorner ? "text-[0.6rem]" : "text-[0.48rem]",
					)}
				>
					{square.name}
				</span>

				{/* Price */}
				{square.price !== null && !isCorner && (
					<span className="text-[0.45rem] text-gray-500">
						{square.type === "tax" ? `$${square.price}` : `$${square.price}`}
					</span>
				)}

				{/* House / hotel indicators */}
				{propertyState && !propertyState.mortgaged && (
					<div className="flex gap-0.5">
						{propertyState.hotel ? (
							<div className="h-2 w-2 rounded-sm bg-red-600" title="Hotel" />
						) : (
							Array.from({ length: propertyState.houses }).map((_, i) => (
								<div
									// biome-ignore lint/suspicious/noArrayIndexKey: static indicators
									key={i}
									className="h-1.5 w-1.5 rounded-sm bg-green-600"
									title="House"
								/>
							))
						)}
					</div>
				)}

				{/* Mortgaged label */}
				{isMortgaged && (
					<span className="text-[0.4rem] font-bold text-gray-400">
						MORTGAGED
					</span>
				)}

				{/* Player tokens */}
				{playerTokens.length > 0 && (
					<div className="flex flex-wrap justify-center gap-0.5">
						{playerTokens.map((p) => (
							<div
								key={p.playerId}
								className={cn(
									"flex h-3 w-3 items-center justify-center rounded-full text-[0.4rem] font-bold text-white",
									PLAYER_COLORS[p.colorIndex % PLAYER_COLORS.length],
								)}
								title={p.name}
							>
								{p.name[0]?.toUpperCase()}
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	);
}
