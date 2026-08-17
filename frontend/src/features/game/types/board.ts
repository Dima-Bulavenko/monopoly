export enum SquareType {
	GO = "go",
	PROPERTY = "property",
	COMMUNITY_CHEST = "community_chest",
	TAX = "tax",
	RAILROAD = "railroad",
	CHANCE = "chance",
	JAIL = "jail",
	UTILITY = "utility",
	FREE_PARKING = "free_parking",
	GO_TO_JAIL = "go_to_jail",
}

export enum ColorGroup {
	BROWN = "brown",
	LIGHT_BLUE = "light_blue",
	PINK = "pink",
	ORANGE = "orange",
	RED = "red",
	YELLOW = "yellow",
	GREEN = "green",
	DARK_BLUE = "dark_blue",
}

type SquareBase = {
	index: number;
	name: string;
};

export type Square = SquareBase & {
	square_type:
		| SquareType.GO
		| SquareType.COMMUNITY_CHEST
		| SquareType.CHANCE
		| SquareType.JAIL
		| SquareType.FREE_PARKING
		| SquareType.GO_TO_JAIL;
};

export type PropertySquare = SquareBase & {
	square_type: SquareType.PROPERTY;
	color_group: ColorGroup;
	price: number;
	/** rent[0]=base, [1]=1H, [2]=2H, [3]=3H, [4]=4H, [5]=hotel */
	rent: [number, number, number, number, number, number];
	house_cost: number;
	mortgage_value: number;
};

export type RailroadSquare = SquareBase & {
	square_type: SquareType.RAILROAD;
	price: number;
	mortgage_value: number;
};

export type UtilitySquare = SquareBase & {
	square_type: SquareType.UTILITY;
	price: number;
	mortgage_value: number;
};

export type TaxSquare = SquareBase & {
	square_type: SquareType.TAX;
	amount: number;
};

export type AnySquare =
	| Square
	| PropertySquare
	| RailroadSquare
	| UtilitySquare
	| TaxSquare;
