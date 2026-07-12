A new code comment was detected.

Before adding it, reconsider:
- Can the code be made self-explanatory instead? Consider changing variable or function names, reorganizing the code, or creating a readable domain object that encapsulates the logic.
- Does the comment explain WHY rather than restating WHAT?
- Is the comment necessary for a non-obvious constraint, invariant, workaround, security concern, or external dependency? Ensure the comment is not simply stating what the code is doing.
- Ensure the comment is not an AI-added note to the user. All communication with the user should happen through the Claude CLI, NOT through comments. Comments are only for complexity that cannot be made self-explanatory and needs additional context.
- Could this instead be expressed through naming, types, tests, or structure?

Retry the edit. Remove unnecessary comments and retain only comments that add durable information that cannot be communicated clearly in code. This does NOT mean removing every comment; inspect each new comment and retain it when it offers real value.
