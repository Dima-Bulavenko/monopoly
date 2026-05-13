interface JwtPayload {
	sub: string;
	display_name?: string;
	exp?: number;
	[key: string]: unknown;
}

export function decodeJwtPayload(token: string): JwtPayload {
	const parts = token.split(".");
	if (parts.length !== 3) {
		throw new Error("Invalid JWT format");
	}
	const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
	const padded = base64.padEnd(
		base64.length + ((4 - (base64.length % 4)) % 4),
		"=",
	);
	const json = atob(padded);
	return JSON.parse(json) as JwtPayload;
}

export function isTokenExpired(token: string): boolean {
	try {
		const payload = decodeJwtPayload(token);
		if (!payload.exp) return false;
		return Date.now() / 1000 > payload.exp;
	} catch {
		return true;
	}
}
