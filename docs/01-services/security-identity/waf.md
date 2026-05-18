# WAF (Web Application Firewall)

> **One-line summary.** Managed L7 firewall for HTTP/HTTPS. Attach to CloudFront, ALB, API Gateway, App Runner, AppSync, or Verified Access. Enforce custom and managed rule groups.

## TL;DR
- Rule-based filtering at L7 — block, allow, count, CAPTCHA, or challenge requests based on headers, paths, IPs, bodies, geographic origin, rate, or matched managed rule groups.
- **AWS Managed Rule Groups** are the right default — out-of-the-box protection against OWASP Top 10, known bad bots, anonymous IPs, account-takeover patterns.
- **Bot Control** and **Account Takeover Prevention (ATP)** are paid managed rule groups that catch most production attack patterns without you writing rules.
- **Rate-based rules** are the simplest brute-force / scraping mitigation — set a per-IP request budget; WAF blocks abusers automatically.
- Pairs with **Shield Advanced** for DDoS protection at L7.

## When to use it
- Any public web app or API. WAF on CloudFront is the canonical front-line filter.
- APIs receiving customer requests where you want abuse / scraping / brute-force protection.
- Compliance (PCI, SOC 2) auditors expecting a WAF in front of public endpoints.
- Mitigating specific known threats (CVEs, bot scrapers, account takeover attempts) without code changes in your app.

## When NOT to use it
- Internal services with no public exposure — no benefit, WAF only fires on requests that reach it.
- L4 / non-HTTP traffic — WAF doesn't apply; use Network Firewall or AWS Shield Standard for L3/L4.
- Workloads behind NLBs without an HTTP-aware tier — WAF doesn't attach to NLB.

## Key concepts

**Web ACL.** The top-level WAF resource. Contains an ordered list of rules + a default action (`ALLOW` or `BLOCK`). Each rule has a name, priority, condition, and action.

**Rules:**
- **Custom rules** — match on headers, paths, query strings, body, source IP, geographic origin, label-based (rules that set labels other rules can match on).
- **Rate-based rules** — count requests per source IP (or per X-Forwarded-For value, etc.) in a 5-minute sliding window; trigger when count exceeds threshold.
- **Managed rule groups (AWS-Managed and third-party Marketplace)** — pre-built rule bundles maintained by AWS or vendors.

**Managed rule groups (AWS):**
- **Core Rule Set (CRS)** — OWASP Top 10 baseline.
- **Known Bad Inputs** — known exploitation payloads.
- **SQL Injection / Linux / Windows / POSIX OS / PHP / WordPress / etc.** — pattern-specific rule sets.
- **IP reputation lists** — Anonymous IP, Amazon IP reputation.
- **Bot Control** (paid) — bot detection, browser / mobile / signed-bot categorization, CAPTCHA challenges.
- **Account Takeover Prevention (ATP)** (paid) — credential-stuffing detection, compromised credential checks, MFA bypass detection.
- **Account Creation Fraud Prevention** (paid).

**Actions on a rule match:**
- **ALLOW** / **BLOCK** — terminal.
- **COUNT** — just count, useful for shadow / staging mode.
- **CAPTCHA / Challenge** — present a JavaScript challenge or CAPTCHA; allow on pass.
- **Label** — tag the request; later rules can match on labels.

**Logging.** Real-time logs to S3 / CloudWatch Logs / Kinesis Firehose. The "log everything, query later" mode is essential for tuning.

**Firewall Manager.** Manage WAF rules centrally across the AWS Organization. Apply baseline rule sets to every public ALB / CloudFront automatically.

**Sampled requests.** WAF console samples matching requests for the last 3 hours — the first place to look when tuning rules.

## Pricing model

- **Per Web ACL per month** — small flat fee.
- **Per rule per month** — small per-rule fee.
- **Per million requests** — per-request fee that varies by rule type.
- **Managed rule groups** (paid ones — Bot Control, ATP, etc.) — per-rule-group monthly fee + per-million-requests on top.
- **Logging** — pay the destination's ingestion (CloudWatch / S3 / Kinesis).

WAF gets expensive on high-traffic CloudFront distributions, but the cost is usually trivial compared to the engineering time saved by not writing the rules yourself.

## Quotas & limits

- **Web ACLs per Region per account**: 100.
- **Rules per Web ACL**: 1,500 WCUs (Web ACL Capacity Units; each rule has a WCU cost).
- **Rate-based rule threshold**: configurable from 100 to 2,000,000,000 requests per 5-minute window.
- **IP sets per account**: 100 (default).
- **Custom response bodies**: up to 32 per Web ACL.

## Common pitfalls

- **WAF on every internal ALB.** Internal services don't need it; pay only where attackers can reach.
- **No baseline managed rule groups.** Skipping AWS Managed Core Rule Set leaves you exposed to known patterns the rest of the internet is already exploiting.
- **Rules in BLOCK before testing.** A new rule set in BLOCK mode breaks legit users. Run in **COUNT** mode for a week, tune, then flip.
- **Rate-based rule too low.** Triggers on real users (CDN-aware crawls, multi-tab users). Set thresholds based on actual log data.
- **Forgetting `X-Forwarded-For` semantics.** When CloudFront fronts WAF on ALB, the originating IP is in `X-Forwarded-For`, not the SYN source. WAF supports forwarded IPs but configure it explicitly.
- **No logs.** Tuning WAF without logs is guesswork. Send to S3 minimum; Kinesis for real-time analytics.
- **Bot Control on a 1-RPS dev API.** The per-million-requests fee for the paid rule groups doesn't scale down well. Use the free rule groups for low-traffic apps.
- **CAPTCHA on every blocked rule.** UX falls off a cliff. Reserve CAPTCHA for suspicious-but-not-clearly-malicious patterns; BLOCK clear bots outright.

## Pairs well with
- [CloudFront](../networking/cloudfront.md), [ELB](../networking/elb.md), [API Gateway](../networking/api-gateway.md) — common attachment points.
- [Shield Advanced](shield.md) — adds DDoS protection + the DDoS response team; bundles unlimited WAF use on protected resources.
- **AWS Firewall Manager** — org-wide WAF policy.
- **CloudWatch Logs Insights** — query WAF logs for tuning.

## Pairs well with these repo pages
- [CloudFront](../networking/cloudfront.md), [Shield](shield.md).

## Further reading
- [AWS WAF documentation](https://docs.aws.amazon.com/waf/).
- [AWS Managed Rules](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups.html).
- [Bot Control](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-bot.html).
- [Account Takeover Prevention](https://docs.aws.amazon.com/waf/latest/developerguide/aws-managed-rule-groups-atp.html).
- [WAF rate-based rules](https://docs.aws.amazon.com/waf/latest/developerguide/waf-rule-statement-type-rate-based.html).
