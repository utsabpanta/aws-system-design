# TinyURL

> **One-line summary.** TinyURL is the canonical "URL shortener" interview problem. See [`url-shortener.md`](url-shortener.md) for the full design.

## Why two pages for the same problem?

The requirements doc lists both `url-shortener.md` and `tinyurl.md`. They're the same system-design question, asked under two names — TinyURL after the original tinyurl.com (2002), URL shortener as the genericized version (bit.ly, ow.ly, t.co, lnkd.in, etc.).

This page is a thin alias so the file list matches the spec; the full design lives at [`url-shortener.md`](url-shortener.md).

## TL;DR (for the impatient)

- Map `short_code → long_url`. Reads dominate writes ~100:1.
- **DynamoDB** keyed on the short code; **CloudFront** to cache popular redirects; **API Gateway + Lambda** for create / read endpoints.
- Code generation: random base62 with conditional write (privacy-preserving) or counter-based base62 (dense).
- Hot links absorbed by edge cache + DAX; click analytics via **Kinesis Firehose → S3 → Athena**.

## Differences in TinyURL-flavored framings

Some interviewers ask "TinyURL" with a specific tilt:

- **Permalink emphasis** — codes must never be reused even after deletion (use a tombstone row + don't recycle short codes).
- **Custom alias** as a first-class feature.
- **Per-user dashboard** of created links.
- **Analytics on every link** as the primary value-add (not optional).

These are additions to the base URL-shortener design, not different patterns. See [`url-shortener.md`](url-shortener.md) for the architecture; layer the additions on top.

## Architecture

See [`url-shortener.md#high-level-architecture`](url-shortener.md#high-level-architecture) and the [`url_shortener.png`](../../images/interview-designs/url_shortener.png) diagram.

## Further reading

- [`url-shortener.md`](url-shortener.md) — the full design.
- ["Designing Pastebin or Bit.ly", System Design Primer](https://github.com/donnemartin/system-design-primer#design-pastebincom-or-bitly).
