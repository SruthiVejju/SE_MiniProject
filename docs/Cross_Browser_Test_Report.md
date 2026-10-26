# Cross-Browser Compatibility Plan and Results (NFR-6)

Scope: the responsive web client must render and function correctly on the latest two major versions of **Chrome, Firefox and Edge**.

## Design measures taken
- Server-rendered HTML5 (`<!DOCTYPE html>`, UTF-8, responsive viewport meta) in `templates/base.html`.
- Plain CSS (`static/css/hms.css`): flexbox, media queries, no vendor prefixes, no experimental features.
- No JavaScript is required for any workflow; forms use standard controls, including `<input type="date">`.
- No inline scripts/styles, so the strict Content-Security-Policy behaves identically across browsers.
- Automated guard: `core/test_frontend.py` fails if these properties regress.

## Workflows to verify (main user workflows)
| # | Workflow | Role |
|---|---|---|
| W1 | Log in, open home page, read and mark notifications | All |
| W2 | Submit leave/outpass request (validation errors shown inline) | Student |
| W3 | Approve / reject a leave request | Warden |
| W4 | Record visitor entry and exit | Security Guard |
| W5 | Record cash / online fee payment, view receipt | Admin |

## Results matrix
Fill in after running `python manage.py runserver` and walking W1-W5 in each browser. Mark Pass/Fail with the browser's exact version.

| Browser | Version (latest) | Version (previous) | W1 | W2 | W3 | W4 | W5 | Layout at 375px width |
|---|---|---|---|---|---|---|---|---|
| Chrome | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Firefox | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| Edge | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Status:** manual browser execution is pending; only the automated static checks above have been run.
