/*
 * Last Evolution - Eeveeon's signature move (Windwave).
 * Power: 80 + 20 for every different Eevee / Eeveelution in the user's party (max 200).
 * NOTE: Cobblemon joins script lines with spaces, so never use line comments in here.
 */
{
	num: 0,
	accuracy: 100,
	basePower: 80,
	basePowerCallback(pokemon, target, move) {
		const kin = ["eevee", "vaporeon", "jolteon", "flareon", "espeon", "umbreon", "leafeon", "glaceon", "sylveon"];
		const found = [];
		for (const ally of pokemon.side.pokemon) {
			if (!ally || ally === pokemon) continue;
			const base = (ally.baseSpecies.baseSpecies || ally.baseSpecies.name || "").toLowerCase();
			if (kin.includes(base) && !found.includes(base)) found.push(base);
		}
		const bp = Math.min(200, move.basePower + 20 * found.length);
		this.debug("Last Evolution BP: " + bp);
		return bp;
	},
	category: "Special",
	name: "Last Evolution",
	pp: 5,
	priority: 0,
	flags: { protect: 1, mirror: 1 },
	secondary: null,
	target: "normal",
	type: "Normal",
	contestType: "Beautiful"
}
