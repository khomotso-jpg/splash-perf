# dinare-perf — the load tester, and the one rule it broke

A single stdlib-only Python load tester for a Splash surface, run **on demand** from GitHub Actions or a
shell. Public repo, so Actions minutes are free.

## Read this before adding a schedule back

Until 2026-09-30 this ran **every Monday at 06:00 UTC against a Vercel preview host**, and reported SUCCESS
every week. The owner retired Vercel, Render and Supabase on 2026-09-28; the preview host went on answering,
because a stale deployment does, so the check went on passing and the report it posted was a latency profile
of something nobody was serving.

Two things were removed together, and both matter:

- **The schedule.** A recurring green tick nobody reads is a claim, and this one was false.
- **The default `TARGET`.** In the workflow AND in `load-test.py`. A default is *how* it survived — nobody
  typed the URL, so nobody re-read it. `TARGET` is now required and the tester exits with a message rather
  than measuring a host it was not asked about.

A pre-flight step curls the target and fails the job unless it answers 2xx/3xx, so a decommissioned host is
red here instead of a report full of timeouts.

**Re-introducing a schedule is fine once there is a live production URL to point it at — and it comes back
with that URL written in, not with a default.**

## The other lesson worth keeping

GitHub's scheduler is not a monitor. `dinare-uptime` measured it: a 5-minute schedule fired **5 times in 24
hours instead of ~288**. Weekly was within tolerance, but nothing tighter should be trusted here.

## Standards

`dinare-platform/scripts/check-standards.sh dinare-perf` must pass. Commits are Conventional Commits. Work
on `main`; **a push is the owner's call.**
