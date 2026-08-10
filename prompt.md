A new code comment was detected.

The edit has already succeeded. Review the new comment before continuing:
- Can the code be made self-explanatory instead? Consider changing variable or function names, reorganizing the code, types, tests, or in the best case creating a readable domain object that encapsulates the logic.
- If above is impossible, does the comment at least explain WHY rather than restating WHAT?
- Is the comment necessary for a non-obvious constraint, invariant, workaround, security concern, or external dependency? Ensure the comment is not simply stating what the code is doing or reflecting a conversation you recently had with the user.
- Ensure the comment is not an AI-added note to the user. All communication with the user should happen through the Claude CLI, NOT through comments. Comments are only for complexity that cannot be made self-explanatory and needs additional context.

If the comment is valuable exactly as is, leave it unchanged and continue; do not rewrite or remove it merely to satisfy this reminder.

Remove the comment (along with an potential change to the code to make it more readable) if after reviewing the above thoughts, you are confident it doesn't offer value as a comment and can be replaced with more readable code or domain representations.

If the comment adds durable information that cannot be communicated clearly in code, at least attempt to tighten it so it gets the idea across using the minimum number of words.

