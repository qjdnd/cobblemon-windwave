---
name: pokemon-official-art
description: Write image-generation prompts (or generate images) in the official Pokémon artwork style for this Cobblemon Wind Wave project, covering Gen 1–10 looks. Use whenever the user asks for Pokémon, fakemon, regional form, evolution line, shiny variant, or model turnaround concept images, or for prompts that should look like official Pokémon art.
---

# Pokémon official art style

The full analysis and the prompt blocks live in the repo. Read both before writing any prompt:

- `docs/art-style/pokemon-official-style-guide.md`: shared style DNA, per-generation analysis (Gen 1–10), failure modes, QA checklist, Cobblemon workflow
- `docs/art-style/prompt-templates.md`: assembly formula, common blocks, generation modifiers, templates A–F, worked example

## Workflow

1. **Pin down the subject.** Settle the evolution stage, type, one real animal plus one object or element motif, 1–3 silhouette-defining features, and a 3–4 color palette tied to body parts. If the user left these open, choose sensible defaults that fit a Southeast Asian tropical archipelago (Gen 10, Winds/Waves) and state what you chose.
2. **Pick the template.** Use A (official art) by default, C for an evolution line, D for a modeling turnaround, E for a regional form, F for a shiny comparison, and B only when the user asks for a retro Gen 1–2 look.
3. **Pick one generation modifier.** Gen 10 is the default for this project. Don't mix modifiers. Gen 1–2 conflict with the cel-shading STYLE BASE, so use template B for them.
4. **Assemble the prompt in English** as SUBJECT + DESIGN RULES + STYLE BASE + GENERATION MODIFIER + COMPOSITION, plus the NEGATIVE block. For a model with no negative-prompt field, use the sentence version and finish with an "Avoid: …" sentence.
5. **Check before and after generating** against the QA checklist in the guide (section 5): silhouette, at most 4 colors, tapered outlines, one hard shadow plus soft highlights, white background, full body in three-quarter view, no resemblance to an existing species.
6. **Fix failures** with the failure-mode table in the guide (section 4) rather than piling on new keywords.

## Rules

- Describe style traits. Don't put artist names in prompts.
- Treat the Gen 10 legendary leaks (Garuda / Naga) as unconfirmed. Use them only if the user asks.
- Generating images with a paid tool spends the user's credits. Confirm the count and the model before you generate.
- Write explanations to the user in Korean, since this project's docs are in Korean. Keep the prompts themselves in English.
