## Communication audience: agents and humans

For delegated mission work, read and apply
[Builder Communication v1](docs/agent-communication/v1/CONTRACT.md) and its
[examples](docs/agent-communication/v1/EXAMPLES.md). Use the structured JSON
messages for assignments, acknowledgements, progress, blockers and completion
reports through the mission's existing supported communication route.

Read the installed [delivery settings](docs/agent-communication/v1/DELIVERY.md).
Use its configured artifact directory and inline reply budget. For a detailed
report, write the full JSON artifact within the assignment's explicit evidence
write scope, then return a compact completion with its path, SHA256 and limits.
Do not replace the artifact with a long inline response that cannot be collected.
The coordinator must read and verify the referenced file before using its claims.

Choose the format by the established recipient and assignment, not by a channel
name such as `final` or whether the message is visible in a chat window:

- To a coordinator, builder or reviewer agent: use the contract's JSON object,
  with the intended recipient identified and findings inside its fields. Do not
  replace it with a human-style summary, greeting, flowchart or Markdown wrapper.
  A delegated result returned to the coordinator is an agent message even when
  the host delivers it as the builder's final response.
- To a human user: follow the applicable human presentation guidance, including
  concise prose and diagrams where helpful. Do not force the agent JSON envelope
  onto ordinary user replies.

Keep both modes. Human presentation preferences apply to human-facing messages;
this contract applies to agent exchanges, subject to higher-priority instructions.
If both audiences need an update, use their existing authorized routes separately
and keep claims consistent. Do not send extra messages without authority. If the
recipient is unclear, establish it before dispatch rather than guessing a route.

Include concise plain-English findings inside the structured fields. Preserve
assignment identity, exact source identity, evidence references and unresolved
limits. Receipt, execution, reported completion, verification and owner acceptance
are distinct claims. Never infer authority or successful execution from syntax.

Existing repository instructions, permissions and product requirements remain
governing. Message format grants no execution or communication authority.
