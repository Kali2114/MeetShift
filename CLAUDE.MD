# MeetShift - Claude Instructions

## General

This is a production Django application.

Before modifying any code:

- explain your plan,
- wait for my approval,
- keep changes minimal,
- never perform large refactors unless explicitly requested.

## Code style

- Follow existing project conventions.
- Preserve naming consistency.
- Do not change formatting of unrelated code.
- Remove unused imports only in modified files.

## Architecture

- Prefer service layer over duplicated business logic.
- Follow existing project architecture.
- Avoid introducing unnecessary abstractions.
- Explain architectural trade-offs before changing them.

## Testing

- Update or add tests for every functional change.
- Do not reduce coverage.
- Prefer TDD when implementing new features.

## Security

- Never introduce development fallbacks into production code.
- Explain every security-related change.
- Prefer fail-fast configuration.

## Git

- Keep changes small.
- One logical change per commit.
- Explain commit purpose.

## Reviews

When reviewing code:

- cite exact file and line,
- explain why it is an issue,
- estimate severity,
- propose a fix,
- distinguish facts from assumptions.

## Communication

If you're uncertain:

- ask,
- do not guess.

If you find multiple issues:

- prioritize them,
- explain impact,
- fix one logical issue at a time.

## Teaching

When making non-trivial changes:

- explain why,
- explain alternatives,
- explain why your solution is preferred.
