A new code comment was detected.

The edit has already succeeded. Work through the following steps in order, and stop at the first one that applies:

1. Refactor first. Ask whether the comment is compensating for a bad name or tangled logic. If a rename, extraction, or reorganization would make the comment unnecessary, do that now and delete the comment — even if it costs more than one edit or touches call sites beyond this line. This is the preferred outcome. Examples: extract a well-named function/predicate instead of commenting what a block does; rename a variable/parameter so it carries the meaning the comment stated; extract a named constant or comparator instead of commenting a magic value or ordering rule; reorder or flatten logic so intent reads top-to-bottom without narration.
2. Remove if it's noise. If the comment restates what the code does, states the obvious, or is an AI-added note to the user (e.g. explaining what you changed or why), delete it. All communication with the user happens through the Claude CLI, never through comments.
3. A comment earns its place only if it explains a WHY the code itself cannot express through any reasonable code change. Currently explaining a why is not enough to keep it — always attempt a refactor first, and only keep the comment if you're confident no rename or restructuring removes the need for it.
4. Tighten the comment only if step 1 was genuinely impossible. Before tightening, double-check: is there really no name or restructuring that would make this comment unneeded? If not, trim it to the minimum words that still get the idea across.
5. If the comment offers legitimate value, keep it only as a last resort.
