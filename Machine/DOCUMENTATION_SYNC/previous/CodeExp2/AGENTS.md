# Agent Workflow Review Guide

When asked to review how an LLM-driven CLI works in a repository, trace the implemented path from the user's request to work in the repository and back. Keep component roles explicit: the model generates a response or structured tool request; the CLI harness assembles context, checks and routes requests, runs tools through an execution environment, and returns tool results to the model as new context.

## Review procedure

1. Find the instruction files the CLI loads, including root and nested `AGENTS.md` files. Identify how those instructions enter the model's context.
2. Find the documented entry command and trace it through launch scripts, command dispatchers, harness code, permission checks, tool definitions, and the tool executor.
3. Verify where commands actually execute, what environment and access they receive, and how results return to the model. Distinguish the model's generated request from the harness's decision and the tool's execution.
4. Compare the implementation with the docs. Check identity and session setup, receipts, permissions, work admission, and whether initialization changes state. Do not infer behavior from names or descriptions alone.
5. Begin with read-only inspection and status/help commands. Read the implementation before running setup, claim, or delivery commands, since they may write files or change coordination state.
6. If behavior and documentation disagree, identify the layer that owns the behavior, make a targeted correction there, update the related documentation, and use the existing focused validation route when available.

Report the observed chain and the specific mismatch before describing any repair. Keep changes within the requested scope. Do not broaden tool access or treat session initialization as permission to perform repository work.
