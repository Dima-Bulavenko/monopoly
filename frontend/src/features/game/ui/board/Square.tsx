import type React from "react";
import type {
	PropertySquare,
	RailroadSquare,
	Square,
	TaxSquare,
	UtilitySquare,
} from "#/client/types.gen";

type AnySquare =
	| PropertySquare
	| RailroadSquare
	| UtilitySquare
	| TaxSquare
	| Square;

type Side = "bottom" | "top" | "left" | "right" | "corner";

type SquareProps = {
	square: AnySquare;
	side: Side;
	style?: React.CSSProperties;
};

const COLOR_GROUP_MAP: Record<string, string> = {
	brown: "#955436",
	light_blue: "#aae0fa",
	pink: "#d93a96",
	orange: "#f7941d",
	red: "#ed1b24",
	yellow: "#fef200",
	green: "#1fb25a",
	dark_blue: "#0072bb",
};

const COLOR_STRIP_SIDE: Record<Side, string> = {
	bottom: "h-1/4 w-full border-b border-black",
	top: "h-1/4 w-full border-t border-black",
	left: "w-1/4 h-full border-r border-black",
	right: "w-1/4 h-full border-l border-black",
	corner: "",
};

const STRIP_POSITION: Record<Side, string> = {
	bottom: "flex-col",
	top: "flex-col-reverse",
	left: "flex-row-reverse",
	right: "flex-row",
	corner: "flex-col items-center justify-center",
};

function ColorStrip({ color, side }: { color: string; side: Side }) {
	return (
		<div
			className={COLOR_STRIP_SIDE[side]}
			style={{ backgroundColor: color }}
		/>
	);
}

function SquareName({ name }: { name: string }) {
	return (
		<div className="flex flex-1 items-center justify-center overflow-hidden p-0.5">
			<span
				className="text-center font-medium leading-tight"
				style={{ fontSize: "clamp(5px, 0.8cqi, 10px)" }}
			>
				{name}
			</span>
		</div>
	);
}

export function BoardSquare({ square, side, style }: SquareProps) {
	const baseClass =
		"border border-black overflow-hidden flex @container " +
		STRIP_POSITION[side];

	if (square.square_type === "property") {
		const color =
			COLOR_GROUP_MAP[(square as PropertySquare).color_group] ?? "#ccc";
		return (
			<div className={baseClass} style={style}>
				<ColorStrip color={color} side={side} />
				<SquareName name={square.name} />
			</div>
		);
	}

	if (
		square.square_type === "go" ||
		square.square_type === "jail" ||
		square.square_type === "free_parking" ||
		square.square_type === "go_to_jail"
	) {
		return (
			<div className={baseClass} style={style}>
				<span
					className="text-center font-bold leading-tight"
					style={{ fontSize: "clamp(6px, 1cqi, 12px)" }}
				>
					{square.name}
				</span>
			</div>
		);
	}

	return (
		<div className={baseClass} style={style}>
			<SquareName name={square.name} />
		</div>
	);
}
