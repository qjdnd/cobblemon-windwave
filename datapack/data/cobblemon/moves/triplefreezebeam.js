/*
 * Triple Freeze Beam - Threiscue's signature move (Windwave).
 * One beam from each of the three ice cubes: hits 3 times, 10% freeze chance per hit.
 */
{
	num: 0,
	accuracy: 90,
	basePower: 35,
	category: "Special",
	name: "Triple Freeze Beam",
	pp: 10,
	priority: 0,
	flags: { protect: 1, mirror: 1 },
	multihit: 3,
	secondary: {
		chance: 10,
		status: "frz"
	},
	target: "normal",
	type: "Ice",
	contestType: "Beautiful"
}
