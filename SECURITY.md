# Security Policy

## Supported version
The latest version on `main` receives security fixes.

## Security model
Docker Doctor performs static, read-only inspection of supported Docker project files. It does not invoke Docker, build images, start containers, execute project code, contact registries, or upload inspected content.

Findings are heuristics and are not a substitute for image vulnerability scanning, secret scanning, runtime hardening, or a security review.

## Reporting a vulnerability
Please use GitHub's private security reporting feature when available. Do not include real credentials, tokens, private configuration, or other sensitive material in a public issue.
