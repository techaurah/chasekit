# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | Yes |

## Reporting a vulnerability

Do not open a public issue for a vulnerability. Report privately via
GitHub Security Advisories on this repository ("Report a vulnerability"
under the Security tab), or email the maintainers through the contact
route at https://techaurah.com.

Expect an acknowledgement within a few days. Confirmed issues are fixed
in a patch release with the reporter credited, unless they prefer
otherwise.

## Notes for this project

ChaseKit handles debtor contact details and financial amounts. Chase
logs (SQLite files) and CSV exports contain personal data: keep them out
of version control (the shipped `.gitignore` excludes `*.db` and `.env`)
and treat them under your own data-protection obligations. SMTP and API
credentials belong in environment variables, never in config files
committed to a repository.
