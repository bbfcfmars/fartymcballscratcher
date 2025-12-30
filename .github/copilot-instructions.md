# GitHub Copilot Instructions

## Project Overview

This is a minimal demonstration repository that showcases GitHub security scanning capabilities with Amplify Security. The repository serves as a testing ground for security workflows and GitHub Actions integrations.

## Tech Stack

- **CI/CD:** GitHub Actions
- **Security Scanning:** Amplify Security Runner
- **License:** MIT License (2025)

## Coding Standards

- Follow standard GitHub Actions workflow syntax and best practices
- Use YAML format for workflow files with proper indentation (2 spaces)
- Include descriptive names for workflows, jobs, and steps
- Add appropriate permissions to workflow files (principle of least privilege)
- Use the latest stable versions of GitHub Actions

## Project Structure

```
.
├── .github/
│   ├── copilot-instructions.md    # This file - Copilot configuration
│   └── workflows/
│       └── amplify.yml             # Amplify Security scanning workflow
└── LICENSE                         # MIT License
```

### Key Files

- **`.github/workflows/amplify.yml`**: Configures automated security scanning using Amplify Security Runner on pull requests, pushes to main/master branches, and manual workflow dispatches.
- **`LICENSE`**: MIT License file for the repository.

## Development Guidelines

### GitHub Actions Workflows

- All workflow files should be placed in `.github/workflows/`
- Use descriptive workflow names that explain their purpose
- Include trigger conditions (`on:`) that make sense for the workflow's purpose
- Set appropriate permissions using the `permissions:` key
- Use conditional execution with `if:` to avoid unnecessary workflow runs
- Prefer official GitHub Actions (e.g., `actions/checkout@v4`) over third-party alternatives when available

### Security Best Practices

- Always review security scan results from Amplify Security
- Keep workflow actions up to date
- Use specific version tags or SHAs for actions rather than branch references (except for trusted sources)
- Minimize permissions granted to workflows
- Avoid storing secrets in code - use GitHub Secrets for sensitive data

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Amplify Security Runner](https://github.com/amplify-security/runner-action)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [YAML Syntax for GitHub Actions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

## Additional Context

This repository is intended for testing and demonstration purposes. When suggesting changes:

- Keep modifications minimal and focused
- Ensure changes maintain security scanning functionality
- Follow GitHub Actions best practices
- Test workflow changes carefully to avoid breaking the CI/CD pipeline
