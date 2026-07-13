A new code comment was detected.

The edit has already succeeded. Review the new comment before continuing:
- Can the code be made self-explanatory instead? Consider changing variable or function names, reorganizing the code, or creating a readable domain object that encapsulates the logic.
- Does the comment explain WHY rather than restating WHAT?
- Is the comment necessary for a non-obvious constraint, invariant, workaround, security concern, or external dependency? Ensure the comment is not simply stating what the code is doing.
- Ensure the comment is not an AI-added note to the user. All communication with the user should happen through the Claude CLI, NOT through comments. Comments are only for complexity that cannot be made self-explanatory and needs additional context.
- Could this instead be expressed through naming, types, tests, or structure?

Remove the comment if it restates the code, narrates the edit, communicates with the user, or can be replaced by clearer naming, types, tests, or structure.

Retain the comment if it adds durable information that cannot be communicated clearly in code, such as the reason for a non-obvious constraint, invariant, workaround, security decision, or external dependency. If it is justified, leave it unchanged and continue; do not rewrite or remove it merely to satisfy this reminder.
