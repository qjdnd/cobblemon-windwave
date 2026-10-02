/*
 * Purify - Cleaweed's ability (Windwave).
 * Poison-type moves become Water-type and get a 1.2x boost (like Refrigerate), and the holder cannot be poisoned.
 */
{
	onModifyTypePriority: -1,
	onModifyType(move, pokemon) {
		if (move.type === "Poison" && !(move.isZ && move.category !== "Status") && !(move.name === "Tera Blast" && pokemon.terastallized)) {
			move.type = "Water";
			move.typeChangerBoosted = this.effect;
		}
	},
	onBasePowerPriority: 23,
	onBasePower(basePower, pokemon, target, move) {
		if (move.typeChangerBoosted === this.effect) return this.chainModify([4915, 4096]);
	},
	onUpdate(pokemon) {
		if (pokemon.status === "psn" || pokemon.status === "tox") {
			this.add("-activate", pokemon, "ability: Purify");
			pokemon.cureStatus();
		}
	},
	onSetStatus(status, target, source, effect) {
		if (status.id !== "psn" && status.id !== "tox") return;
		if (effect && effect.status) {
			this.add("-immune", target, "[from] ability: Purify");
		}
		return false;
	},
	flags: { breakable: 1 },
	name: "Purify",
	rating: 3,
	num: 0
}
