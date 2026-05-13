export type SquareType =
	| "property"
	| "railroad"
	| "utility"
	| "tax"
	| "card"
	| "corner";

export type ColorGroup =
	| "brown"
	| "light-blue"
	| "pink"
	| "orange"
	| "red"
	| "yellow"
	| "green"
	| "dark-blue"
	| null;

export interface BoardSquareData {
	index: number;
	name: string;
	type: SquareType;
	colorGroup: ColorGroup;
	price: number | null;
	mortgageValue: number | null;
}

export const BOARD_SQUARES: BoardSquareData[] = [
	{
		index: 0,
		name: "GO",
		type: "corner",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 1,
		name: "Mediterranean Ave",
		type: "property",
		colorGroup: "brown",
		price: 60,
		mortgageValue: 30,
	},
	{
		index: 2,
		name: "Community Chest",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 3,
		name: "Baltic Ave",
		type: "property",
		colorGroup: "brown",
		price: 60,
		mortgageValue: 30,
	},
	{
		index: 4,
		name: "Income Tax",
		type: "tax",
		colorGroup: null,
		price: 200,
		mortgageValue: null,
	},
	{
		index: 5,
		name: "Reading Railroad",
		type: "railroad",
		colorGroup: null,
		price: 200,
		mortgageValue: 100,
	},
	{
		index: 6,
		name: "Oriental Ave",
		type: "property",
		colorGroup: "light-blue",
		price: 100,
		mortgageValue: 50,
	},
	{
		index: 7,
		name: "Chance",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 8,
		name: "Vermont Ave",
		type: "property",
		colorGroup: "light-blue",
		price: 100,
		mortgageValue: 50,
	},
	{
		index: 9,
		name: "Connecticut Ave",
		type: "property",
		colorGroup: "light-blue",
		price: 120,
		mortgageValue: 60,
	},
	{
		index: 10,
		name: "Jail / Just Visiting",
		type: "corner",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 11,
		name: "St. Charles Place",
		type: "property",
		colorGroup: "pink",
		price: 140,
		mortgageValue: 70,
	},
	{
		index: 12,
		name: "Electric Company",
		type: "utility",
		colorGroup: null,
		price: 150,
		mortgageValue: 75,
	},
	{
		index: 13,
		name: "States Ave",
		type: "property",
		colorGroup: "pink",
		price: 140,
		mortgageValue: 70,
	},
	{
		index: 14,
		name: "Virginia Ave",
		type: "property",
		colorGroup: "pink",
		price: 160,
		mortgageValue: 80,
	},
	{
		index: 15,
		name: "Pennsylvania Railroad",
		type: "railroad",
		colorGroup: null,
		price: 200,
		mortgageValue: 100,
	},
	{
		index: 16,
		name: "St. James Place",
		type: "property",
		colorGroup: "orange",
		price: 180,
		mortgageValue: 90,
	},
	{
		index: 17,
		name: "Community Chest",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 18,
		name: "Tennessee Ave",
		type: "property",
		colorGroup: "orange",
		price: 180,
		mortgageValue: 90,
	},
	{
		index: 19,
		name: "New York Ave",
		type: "property",
		colorGroup: "orange",
		price: 200,
		mortgageValue: 100,
	},
	{
		index: 20,
		name: "Free Parking",
		type: "corner",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 21,
		name: "Kentucky Ave",
		type: "property",
		colorGroup: "red",
		price: 220,
		mortgageValue: 110,
	},
	{
		index: 22,
		name: "Chance",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 23,
		name: "Indiana Ave",
		type: "property",
		colorGroup: "red",
		price: 220,
		mortgageValue: 110,
	},
	{
		index: 24,
		name: "Illinois Ave",
		type: "property",
		colorGroup: "red",
		price: 240,
		mortgageValue: 120,
	},
	{
		index: 25,
		name: "B&O Railroad",
		type: "railroad",
		colorGroup: null,
		price: 200,
		mortgageValue: 100,
	},
	{
		index: 26,
		name: "Atlantic Ave",
		type: "property",
		colorGroup: "yellow",
		price: 260,
		mortgageValue: 130,
	},
	{
		index: 27,
		name: "Ventnor Ave",
		type: "property",
		colorGroup: "yellow",
		price: 260,
		mortgageValue: 130,
	},
	{
		index: 28,
		name: "Water Works",
		type: "utility",
		colorGroup: null,
		price: 150,
		mortgageValue: 75,
	},
	{
		index: 29,
		name: "Marvin Gardens",
		type: "property",
		colorGroup: "yellow",
		price: 280,
		mortgageValue: 140,
	},
	{
		index: 30,
		name: "Go to Jail",
		type: "corner",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 31,
		name: "Pacific Ave",
		type: "property",
		colorGroup: "green",
		price: 300,
		mortgageValue: 150,
	},
	{
		index: 32,
		name: "North Carolina Ave",
		type: "property",
		colorGroup: "green",
		price: 300,
		mortgageValue: 150,
	},
	{
		index: 33,
		name: "Community Chest",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 34,
		name: "Pennsylvania Ave",
		type: "property",
		colorGroup: "green",
		price: 320,
		mortgageValue: 160,
	},
	{
		index: 35,
		name: "Short Line Railroad",
		type: "railroad",
		colorGroup: null,
		price: 200,
		mortgageValue: 100,
	},
	{
		index: 36,
		name: "Chance",
		type: "card",
		colorGroup: null,
		price: null,
		mortgageValue: null,
	},
	{
		index: 37,
		name: "Park Place",
		type: "property",
		colorGroup: "dark-blue",
		price: 350,
		mortgageValue: 175,
	},
	{
		index: 38,
		name: "Luxury Tax",
		type: "tax",
		colorGroup: null,
		price: 75,
		mortgageValue: null,
	},
	{
		index: 39,
		name: "Boardwalk",
		type: "property",
		colorGroup: "dark-blue",
		price: 400,
		mortgageValue: 200,
	},
];

export const COLOR_GROUP_CLASSES: Record<NonNullable<ColorGroup>, string> = {
	brown: "bg-[#955436]",
	"light-blue": "bg-[#aae0fa]",
	pink: "bg-[#d93a96]",
	orange: "bg-[#f7941d]",
	red: "bg-[#ed1b24]",
	yellow: "bg-[#fef200]",
	green: "bg-[#1fb25a]",
	"dark-blue": "bg-[#0072bb]",
};

export const PLAYER_COLORS = [
	"bg-red-500",
	"bg-blue-500",
	"bg-green-500",
	"bg-yellow-400",
	"bg-purple-500",
	"bg-pink-500",
];
