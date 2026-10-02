/*
 * Cleansing Net - Cleaweed's signature move (Windwave).
 * Resets the target's stat stages (like Clear Smog) and cures the user's own status condition.
 */
{
	num: 0,
	accuracy: 100,
	basePower: 80,
	category: "Special",
	name: "Cleansing Net",
	pp: 10,
	priority: 0,
	flags: { protect: 1, mirror: 1 },
	onHit(target) {
		target.clearBoosts();
		this.add("-clearboost", target);
	},
	onAfterHit(target, source) {
		if (source.hp && source.status) source.cureStatus();
	},
	secondary: null,
	target: "normal",
	type: "Water",
	contestType: "Beautiful"
}
