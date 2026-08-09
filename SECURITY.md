# Security Policy

## Scope

This repository contains Docker configuration, ComfyUI workflows, experiment records, and documentation. It does not contain model credentials or model weights by design.

## Reporting a vulnerability

Please do not publish secrets, access tokens, or exploitable details in a public issue. Use [GitHub's private vulnerability reporting](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/security/advisories/new) when available. If that form is unavailable, open a minimal issue asking for a private contact channel without including sensitive material.

Before reporting, check that the issue is caused by this repository rather than an upstream model, ComfyUI release, custom node, or downloaded asset. Include the affected commit, environment, reproduction steps, and a safe impact summary.

## Documentation dependency note

The stable VitePress release currently used for the static documentation build may be reported by `npm audit` through its transitive Vite/esbuild development dependencies. The audit currently reports no available fix for that stable VitePress line. The Pages workflow performs a static build and does not expose the Vite development server; re-check the audit when VitePress publishes a compatible stable update.
