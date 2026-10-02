/*
 * Grave Uprising - Cryptonix's signature move (Windwave).
 * Gravestones and spectral hands rise from the ground; the target is trapped (like Spirit Shackle).
 */
{
	num: 0,
	accuracy: 100,
	basePower: 90,
	category: "Physical",
	name: "Grave Uprising",
	pp: 10,
	priority: 0,
	flags: { protect: 1, mirror: 1 },
	secondary: {
		chance: 100,
		onHit(target, source, move) {
			if (source.isActive) target.addVolatile("trapped", source, move, "trapper");
		}
	},
	target: "normal",
	type: "Ghost",
	contestType: "Tough"
}
