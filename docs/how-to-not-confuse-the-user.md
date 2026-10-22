# How to not confuse the user

Use this guide for human-facing status, completion, diagnosis, review and
handoff messages. Apply the [human-facing visual communication guide](../.agents/guides/human-facing-visual-communication.json)
when a compact illustration would make a material relationship easier to grasp.
It applies alongside Delivery Discipline and does not grant additional execution
authority.

## Default response shape

Lead with the outcome the person asked for, in plain language. Include only
details that change one of these:

1. What they can do now.
2. What is unavailable or failed.
3. A decision or action they need to take.

If none changes, omit the detail. Internal commands, hashes, test counts,
temporary workarounds, tool names and build-pipeline trivia are evidence—not
the answer.

For a simple request, one direct sentence is enough:

> Regenerated successfully. The fresh isolated candidate is ready for review.

## Relevance filter

Before sending, ask:

- Did the user ask for this detail, or does it materially change their next action?
- Would a non-expert understand why it matters without additional explanation?
- Does it alter availability, correctness, safety, cost, timing, or authority?

If the answer is no, leave it out. Keep the evidence available for verification;
do not put it in the lead.

## Exceptions and failures

Mention an internal failure only when it prevents the requested outcome,
degrades it, creates risk, or requires a user decision. State the consequence
first, then the minimum useful cause.

Good:

> The app was not regenerated because packaging failed before an artifact was created.

Not useful unless asked:

> `iconutil` rejected an iconset, but the requested artifact was regenerated
> with approved existing bytes.

The second statement may belong in evidence, not the user-facing result.

## Evidence on demand

Keep reports, hashes, test output and limitations accurate and retrievable.
Offer or provide them when the user asks for verification, diagnosis, release
provenance, or a technical handoff. Do not make the user parse them to discover
the outcome.

## Completion check

Before responding, verify that the first sentence answers the user’s request.
Then state a limitation only if it changes the practical result. If there is no
such limitation, stop.

This is an agent-interpreted communication guide. It improves reporting; it
does not replace product acceptance, native verification, or the existing
evidence contracts.
