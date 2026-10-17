# How not to overengineer on your way to the executable runtime target

Instructions for agents implementing software in any repository. Apply the shared
rules in [Delivery Discipline](delivery-discipline.md) and the repository's
requirements. Use the [plan guide](how-to-follow-and-refresh-a-plan.md) when
following or changing a plan and the [coordinator guide](how-to-coordinate-with-a-builder-agent.md)
when work is delegated. This guide owns the runtime-integration procedure; it
grants no additional permissions and does not relax safety or execution invariants.

Your responsibility is to reach the user's executable runtime target with the
smallest sufficient implementation. Keep development connected to that target
throughout the work.

1. **Define the executable finish line.** Before implementation, identify the
   user's starting action, the real components involved, the expected result and
   how you will observe it. Include required lifecycle, recovery and presentation
   behavior. Keep this short. For example: "Open the app, select a project, launch
   the actual CLI in that folder, and display its live state and output." Do not
   replace this with "implement the adapter" or "pass the checks."

2. **Test the assumption that can kill the design first.** Inspect the actual
   interface, then run the smallest authorized experiment against the real
   dependency. Establish that the process can start and the required interaction
   is supported before building layers around it. Documentation, method names,
   mocked responses and successful compilation leave runtime compatibility
   unproven. If the experiment is blocked, explain the specific missing access or
   capability promptly. Establish the safeguards needed for that experiment's
   effects first. An authorized diagnostic launch does not prove an automatic
   workflow, and a denied route must not be bypassed to obtain a demonstration.

3. **Build one complete, narrow path.** Connect one real input to one real result
   through the intended entry point. Use the minimum presentation needed for the
   user's scenario. Include the failure handling necessary to run that path
   safely. Extend this working path incrementally. Avoid implementing many
   disconnected components and postponing their first integration until the end.

4. **Make additional machinery justify itself.** Before adding a component,
   abstraction, dependency or persistent record, identify the concrete runtime
   step it enables and why the existing implementation cannot do that adequately.
   Prefer a direct call, a small function or an edit at the owning layer when
   sufficient. Add general provider systems, event buses, state machines,
   provenance stores or dashboards when the current requirements demonstrate
   their need. Anticipated future uses alone do not justify them.

5. **Repair the observed failure at its source.** Reproduce the failure, identify
   the responsible layer, change the smallest relevant implementation, then rerun
   the failed real interaction. Preserve useful diagnostic evidence in the
   existing structure. Do not make each failure a new versioned project with its
   own specification, framework, approval system and test universe. If a repair
   requires an architecture change, explain that consequence before expanding
   scope.

6. **Stop repair loops before they consume the project.** Apply Delivery
   Discipline's [shared repair limit](delivery-discipline.md#shared-repair-limit).
   Keep the original runtime target while moving to an evidenced alternative
   within authorized scope. Bring material changes to the user; do not require a
   new approval for a routine implementation choice already covered by that scope.

7. **Keep safeguards at the relevant boundary.** Preserve required checks,
   permissions, reviews and automatic recovery. Integrate them into the narrow
   runtime path. Apply commit checks to the changes they govern; ordinary
   documentation maintenance should not require a runtime launch or a special
   exception for each commit. Do not invent blanket repository freezes or new
   approval layers. If an existing requirement blocks the target, identify it
   explicitly. Resolve the conflict within the user's authority rather than
   bypassing it or constructing an unrelated deliverable.

8. **Use tests to answer concrete questions.** Run the focused checks needed for
   the changed behavior, its material failure cases and required invariants. Use
   fakes for isolated logic and actual integration for compatibility claims.
   Once checks pass, return to the runtime target. Broaden testing when a new
   failure, change or material uncertainty warrants it. Increasing test counts
   does not compensate for an absent process or an unexecuted user flow.

9. **Demonstrate the result through the real entry point.** Verify that the
   intended process is alive, receives the input and produces the expected
   result. Exercise required shutdown or recovery behavior. A saved session, a
   queue acknowledgement or a completed receipt alone cannot establish this.
   When the workflow requires automatic execution, manual startup, relay or
   cleanup leaves that acceptance condition unmet.

10. **Report the distance to the target honestly.** State what the user can now
    run, how it was verified and which required behavior remains unavailable.
    Give the actual launch command or user action when applicable. Label an
    unexecuted or incomplete path as partial or blocked. Do not announce success
    for scaffolding while quietly moving the executable target to another task.

Before continuing work, ask yourself: **Does this next change directly enable or
verify the requested runtime behavior?** If you cannot name the connection,
reassess the change before spending the user's time on it.

Apply these instructions through ordinary engineering judgment. Do not build an
enforcement framework, scoring system or approval process to demonstrate that you
are avoiding overengineering.
