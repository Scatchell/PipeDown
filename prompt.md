A new code comment was detected.

The edit has already succeeded. Work through the following steps in order, and stop at the first one that applies:

1. Refactor first. Ask whether the comment is compensating for a bad name or tangled logic. If a rename (variable, function, type), a small extraction, or a light reorganization would make the comment unnecessary, do that refactor now and delete the comment. This is the preferred outcome — prefer it even if it costs more than one edit or touches call sites beyond this line.
2. Remove if it's noise. If the comment merely restates what the code does, states the obvious, or is an AI-added note to the user (e.g. explaining what you changed or why), delete it. All communication with the user happens through the Claude CLI, never through comments. Anything that looks like it could be interpretted as a note to the user or about a recent question they've asked should immediately be removed.
3. A comment earns its place only if it explains a WHY the code itself simply CAN NOT express through a code changes making it more readable. DO NOT keep a comment just because it currently explains a why, that is not enough. Only keep it if the why it explains cannot reasonable be expressed through code. Always attempt to alter the code first to make it more readable before giving up and keeping the comment.
4. Tighten the comment only if the above is not possible. You should only reach this step if step 1 was genuinely impossible. Before tightening, go back and double check: is there really no name or restructuring that would make this comment unneeded? If you're confident there isn't, trim the comment to the minimum words that still get the idea across.
5. If the comment offers legitimate value, keep it only as a last resort.
