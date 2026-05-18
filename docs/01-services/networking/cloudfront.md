# CloudFront

> **One-line summary.** AWS's global content delivery network. Caches at hundreds of edge POPs, terminates TLS, runs lightweight logic at the edge, and shields origins from load.

## TL;DR
- Sits in front of any HTTP / WebSocket / gRPC origin (S3, ALB, EC2, API Gateway, MediaPackage, or arbitrary URL). Caches what's cacheable, forwards what isn't.
- **Anything user-facing belongs behind CloudFront**, even single-Region origins — TLS termination at the edge is faster, the AWS backbone is more reliable than the public internet, and origin egress to CloudFront is free (unlike egress straight to the user).
- Two flavors of edge compute: **CloudFront Functions** (microsecond JavaScript at the edge, for simple header / URL manipulations) and **Lambda@Edge** (full Lambda at four select POPs, for richer logic that's OK with millisecond-scale latency).
- **Origin Access Control (OAC)** is the modern way to lock an S3 origin to a CloudFront distribution; never use a public S3 bucket as origin.
- **Signed URLs / signed cookies** for private content; **field-level encryption** for PCI-style data; **WAF + Shield Advanced** integrate natively.

## When to use it
- Any public web app, API, or media delivery.
- Cache static assets (S3 + CloudFront is the canonical static-site stack).
- Reduce origin load and per-GB egress cost — outbound from S3 / EC2 to CloudFront is free.
- Edge logic: A/B test bucketing, header rewriting, auth checks, geo blocking.
- DDoS mitigation: Shield Standard is free and on by default; Shield Advanced adds L7 protection and a dedicated response team.
- Video streaming, large file downloads, software updates.

## When NOT to use it
- Strictly private internal services that never serve external users — CloudFront is an internet-facing edge.
- Workloads where per-request edge compute latency *and* cost is unwanted (a CloudFront distribution per micro-app is fine; ten layers of edge logic per request is not).
- Workloads with extreme bandwidth-cost sensitivity at a single Region — sometimes serving directly from an in-Region cluster is cheaper than CloudFront's per-GB rates, though that's rare once you factor TLS, AWS Shield, and operational simplification.

## Key concepts

**Distribution.** The CloudFront resource. Has one or more **origins** (where to fetch from), **behaviors** (path patterns and per-path cache / security / origin config), and a **default behavior** as the fall-through.

**Origin types.**
- **S3 bucket** (with **OAC** — Origin Access Control — for private buckets).
- **ALB / NLB / EC2** — HTTP origin.
- **API Gateway** — REST or HTTP API behind CloudFront.
- **MediaPackage / MediaStore** — video.
- **Lambda function URL** — direct.
- **Custom origin** — any URL (cross-cloud, on-prem).

**Origin Access Control (OAC).** Replaces the older OAI (Origin Access Identity). Signs requests to S3 with SigV4; supports KMS-encrypted buckets, cross-account, and Lambda function URLs. Always OAC for new distributions.

**Behaviors.** Path patterns (`/images/*`, `*.js`) that map to a specific origin, cache policy, origin request policy, response headers policy, and edge functions. The default behavior (`*`) is the catch-all.

**Cache key.** Defines what makes a cache hit unique. Includes the URL by default; **Cache Policies** let you include selected headers, query strings, or cookies in the key. **Origin Request Policies** decide what to forward to the origin (which can be a superset of the cache key).

**Edge compute:**
- **CloudFront Functions** — JavaScript, sub-millisecond, runs at every edge POP. Limited runtime (~1 ms CPU, no network calls); for header manipulation, URL rewrites, simple auth, cache key normalization.
- **Lambda@Edge** — full Lambda runtime, Node.js / Python, runs at the four nearest Regional Edge Caches. Millisecond-scale latency; can make network calls. For richer logic (token introspection, dynamic content assembly).

**Cache invalidation.** `CreateInvalidation` flushes specific path patterns. The first 1,000 invalidation paths per month are free; after that, per-path fee. Prefer cache versioning (`/v2/asset.js` instead of invalidating `/asset.js`) for high-churn assets.

**Real-time logs and standard logs.** Standard logs delivered to S3 (~minutes lag); real-time logs to Kinesis Data Streams for sub-second observability.

**Origin Shield.** Optional caching layer between edge POPs and origin in one chosen Region — improves cache hit ratio for origins with many distributed edges drawing from them, and reduces origin load.

**Continuous deployment.** Test a "staging distribution" with a copy of production config, route a small slice of traffic to it via weighted Continuous Deployment Policies, promote on success.

**HTTP/3 (QUIC), HTTP/2.** Both enabled by default; faster page loads and better mobile performance.

## Pricing model

- **Per-GB transferred out to internet** — Region-tiered (cheaper in NA/Europe, more in Asia, more in South America / India). **No data transfer charges from S3 / EC2 / ALB origins to CloudFront** — that's the free piece.
- **Per HTTPS request** — small per-10,000.
- **CloudFront Functions** — per million invocations (cheap).
- **Lambda@Edge** — per request + per GB-second (more expensive than regular Lambda).
- **Invalidations** — 1,000 paths/month free, then per-path.
- **Real-time logs** — per-line published to Kinesis.
- **Origin Shield** — adds per-request fee for the shielded region's tier.
- **Shield Standard** — free; **Shield Advanced** — significant monthly fee, includes WAF and the DDoS response team.

The economic case is straightforward: **CloudFront egress is cheaper than direct origin egress** for most Regions, and the cache hit ratio further reduces origin load.

## Quotas & limits

- **Distributions per account**: 200 default (raisable to thousands).
- **Behaviors per distribution**: 25 default (raisable).
- **Origins per distribution**: 25.
- **Cache policies / origin request policies / response headers policies per account**: 20 each (raisable).
- **CloudFront Function size**: 10 KB.
- **Lambda@Edge package size**: 1 MB compressed (viewer event), 50 MB unzipped (origin event).
- **Max object size**: 30 GB.

## Common pitfalls

- **Public S3 origin instead of OAC.** Anyone with the S3 URL can bypass CloudFront. Always OAC.
- **Skipping CloudFront for "single Region anyway" apps.** TLS at the edge, free origin-to-CF transfer, Shield Standard, and consistent global latency are wins even in single-Region setups.
- **Cache key includes everything.** Forwarding all headers / all query strings to the cache key destroys hit ratio. Pick the specific dimensions that vary content.
- **Cache invalidation as a deploy step.** Per-path fees add up; also, invalidations are slow (~minutes). Use cache versioning in URLs instead.
- **Lambda@Edge for simple header tweaks.** Use CloudFront Functions — cheaper, faster, doesn't span Region boundaries.
- **Forgetting `Vary` for personalized content.** Two users see each other's personalized responses because the cache key didn't account for the auth header. Either bypass cache for personalized paths or add the right dimensions to the cache key.
- **No `error caching min TTL`.** Backend hiccup → CloudFront caches a 500 for 5 minutes by default. Lower it for paths where you want errors to recover quickly.
- **Origin Shield in the wrong Region.** Pick the Region closest to your origin, not a random one.
- **Continuous Deployment unused.** Rolling distribution config changes globally is risky. Use the staging distribution + traffic split.

## Pairs well with
- [S3](../storage/s3.md) — the canonical static-content origin.
- [API Gateway](api-gateway.md) — CloudFront in front of HTTP API / REST API.
- [Route 53](route53.md) — DNS alias to the distribution.
- **AWS WAF** — managed rule groups + custom rules.
- **AWS Shield Standard / Advanced** — DDoS protection.
- **AWS Certificate Manager (ACM)** — free TLS certs (must be in `us-east-1` for CloudFront).
- **Lambda@Edge / CloudFront Functions** — edge logic.

## Pairs well with these repo pages
- [Global Accelerator](global-accelerator.md) — non-HTTP global routing.
- `docs/04-reference-architectures/static-website-s3-cloudfront.md` (forthcoming).

## Further reading
- [Amazon CloudFront documentation](https://docs.aws.amazon.com/cloudfront/).
- [Origin Access Control (OAC)](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html).
- [CloudFront Functions vs Lambda@Edge](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/edge-functions.html).
- [Cache policies and origin request policies](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/working-with-policies.html).
- [Origin Shield](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/origin-shield.html).
