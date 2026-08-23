# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

[Add a brief description of the project's purpose and scope. Keep it to 2-3 sentences.]

## Development Setup

### Prerequisites
[Document any required tools, versions, or environment setup needed before development begins.]

### Installation
[Provide step-by-step instructions for setting up a local development environment.]

### Environment Variables
[If applicable, document required environment variables and how to configure them. Never include actual secrets in this file.]

## Build & Development Commands

### Build
```bash
# [Add your build command here]
```

### Running Tests
```bash
# Run all tests
# [Add your test command]

# Run a single test
# [Add your single test command]

# Watch mode (if applicable)
# [Add your watch command]
```

### Linting & Formatting
```bash
# Lint code
# [Add your lint command]

# Format code
# [Add your format command]

# Check formatting without fixing
# [Add your format check command]
```

### Running the Application
```bash
# Start development server / run app
# [Add your dev/run command]

# Build for production
# [Add your production build command]
```

## Architecture & Codebase Structure

### High-Level Architecture
[Describe the overall system architecture. Answer questions like:
- What are the main components/layers?
- How do they interact?
- What design patterns are used?
- Why were certain architectural decisions made?]

### Directory Structure
[Describe the logical organization of the codebase, not just a directory listing. Explain:
- What lives in each major directory/module
- Why it's organized this way
- Key interdependencies between parts]

### Key Design Patterns
[Document important patterns used throughout the codebase that developers should be aware of and maintain.]

### External Dependencies
[List and explain significant third-party libraries/frameworks and why they were chosen. Focus on non-obvious dependencies that affect architecture.]

## Development Conventions

### Code Style
[Document any project-specific style conventions beyond what linters enforce. Examples:
- Naming conventions (e.g., interfaces prefixed with `I`)
- Comment styles for specific scenarios
- Import ordering conventions]

### Testing Standards
[Describe testing approach and conventions:
- What should be unit tested vs. integration tested
- Mocking and fixture patterns
- How to name test files]

### Git Workflow
[Document the workflow for this repository:
- Branch naming conventions
- Commit message format
- PR review process]

### API/Interface Design
[If applicable, document conventions for:
- API endpoint naming
- Function/method signatures
- Error handling patterns]

## Common Tasks & Workflows

### Adding a New Feature
[Outline the typical steps and considerations for adding new functionality.]

### Debugging
[Provide tips and common debugging strategies specific to this codebase.]

### Performance Optimization
[Document any performance considerations or optimization techniques relevant to this project.]

## Configuration Files

[Document the purpose and important settings in configuration files like:
- tsconfig.json / webpack.config.js / vite.config.js
- .eslintrc / prettier.config.js
- CI/CD configuration
- Any custom project configs]

## Known Issues & Gotchas

[Document any quirks, limitations, or non-obvious behaviors that developers should be aware of:]

- [Issue/gotcha 1]
- [Issue/gotcha 2]

## Related Documentation

- [README.md](./README.md) - Project overview and quick start
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines (if it exists)
- [Architecture Decision Records](./docs/adr/) - Detailed architectural decisions (if maintained)

## Maintenance Notes

### Updating Dependencies
[Document the process and any special considerations for updating packages.]

### Deprecation Policy
[If applicable, document how the project handles deprecation of features/APIs.]

## Quick Reference

### Useful Commands Summary
[Create a quick lookup table of the most frequently used commands.]

| Task | Command |
|------|---------|
| [Task] | `[command]` |
| [Task] | `[command]` |

