/*
 * Frostsaw - Avalott's signature move (Windwave).
 * Spinning slicing attack: high crit ratio, 10% freeze, clears hazards/binding on the user's side like Rapid Spin.
 */
{
	num: 0,
	accuracy: 100,
	basePower: 80,
	category: "Physical",
	name: "Frostsaw",
	pp: 10,
	priority: 0,
	flags: { contact: 1, protect: 1, mirror: 1, slicing: 1 },
	critRatio: 2,
	onAfterHit(target, pokemon, move) {
		if (!move.hasSheerForce) {
			if (pokemon.hp && pokemon.removeVolatile("leechseed")) {
				this.add("-end", pokemon, "Leech Seed", "[from] move: Frostsaw", "[of] " + pokemon);
			}
			const sideConditions = ["spikes", "toxicspikes", "stealthrock", "stickyweb", "gmaxsteelsurge"];
			for (const condition of sideConditions) {
				if (pokemon.hp && pokemon.side.removeSideCondition(condition)) {
					this.add("-sideend", pokemon.side, this.dex.conditions.get(condition).name, "[from] move: Frostsaw", "[of] " + pokemon);
				}
			}
			if (pokemon.hp && pokemon.volatiles["partiallytrapped"]) {
				pokemon.removeVolatile("partiallytrapped");
			}
		}
	},
	onAfterSubDamage(damage, target, pokemon, move) {
		if (!move.hasSheerForce) {
			if (pokemon.hp && pokemon.removeVolatile("leechseed")) {
				this.add("-end", pokemon, "Leech Seed", "[from] move: Frostsaw", "[of] " + pokemon);
			}
			const sideConditions = ["spikes", "toxicspikes", "stealthrock", "stickyweb", "gmaxsteelsurge"];
			for (const condition of sideConditions) {
				if (pokemon.hp && pokemon.side.removeSideCondition(condition)) {
					this.add("-sideend", pokemon.side, this.dex.conditions.get(condition).name, "[from] move: Frostsaw", "[of] " + pokemon);
				}
			}
			if (pokemon.hp && pokemon.volatiles["partiallytrapped"]) {
				pokemon.removeVolatile("partiallytrapped");
			}
		}
	},
	secondary: {
		chance: 10,
		status: "frz"
	},
	target: "normal",
	type: "Ice",
	contestType: "Cool"
}
