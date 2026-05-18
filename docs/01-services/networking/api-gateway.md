# API Gateway

> **One-line summary.** Managed API front door — HTTP / REST / WebSocket — that handles routing, auth, rate limiting, request validation, and integration to Lambda, ECS, EC2, Step Functions, or any HTTP backend.

## TL;DR
- Three API types: **HTTP API** (cheaper, faster, modern default), **REST API** (older, full-featured), **WebSocket API** (persistent connections, message routing).
- **HTTP APIs are ~71% cheaper and ~60% lower latency than REST APIs** — use HTTP API by default; only reach for REST API when you specifically need its extra features (API keys with usage plans, AWS WAF, request transformations, response caching, the Apigee-style management surface).
- Integrate with **Lambda**, **HTTP endpoints (public or private ALB / NLB / IPs via VPC Link)**, **AWS services directly via SDK integration**, **Step Functions**, **EventBridge**, **SQS / SNS / Kinesis**.
- Built-in **JWT authorizers** (HTTP API) and **Lambda authorizers** (both) cover modern auth without writing repeated code in every Lambda.
- The biggest decision point in 2026 is "HTTP API or REST API" — don't default to REST out of habit.

## When to use it
- Public or internal HTTP APIs fronting Lambda, container services, or other backends.
- WebSocket APIs for chat, real-time updates, IoT control.
- Service-to-service APIs that benefit from managed throttling, auth, and observability without writing them per service.
- "I want to expose a Lambda over HTTPS" — Function URLs are simpler if you don't need anything beyond that; API Gateway when you need routing, auth, rate limits, or aggregation.

## When NOT to use it
- Internal-only service-to-service traffic within one VPC — direct NLB / ALB / Service Connect / PrivateLink is typically cheaper and lower-latency.
- High-throughput, ultra-low-latency endpoints (millions of RPS, sub-ms requirements) — NLB beats API Gateway on raw forwarding.
- WebSockets at extreme scale — API Gateway WebSocket has connection / message limits and pricing that can be beaten by a custom Fargate / EC2 setup at very high concurrency.
- gRPC — API Gateway doesn't natively front gRPC. Use ALB instead.

## Key concepts

### HTTP API
- The modern default. Cheaper and faster than REST API.
- **Routes** — method + path patterns (`POST /orders`, `ANY /pets/{id}`).
- **Integrations** — Lambda (with payload format v2), HTTP endpoint (public or private via VPC Link), AWS service.
- **JWT authorizers** — built-in JWT validation against any OIDC provider (Cognito, Auth0, Okta, Google). No Lambda authorizer needed for the common case.
- **CORS** — first-class config.
- **Stages** — `$default`, custom names (`prod`, `staging`).

### REST API
- The full-featured original. Use when you need:
  - **API keys with usage plans** for per-customer rate limiting and quotas.
  - **AWS WAF integration** (REST API has it directly; HTTP API needs WAF on a CloudFront distribution fronting the API).
  - **Request / response transformations** with mapping templates.
  - **Response caching** at the gateway level.
  - **Per-method throttling**.
  - **Edge-optimized** deployment for CloudFront-fronted global APIs.
  - **Regional** vs **Private** endpoints (Private API only reachable from a specified VPC via Interface endpoint).

### WebSocket API
- Long-lived connections. Routes are based on a **route selection expression** evaluated against the message (e.g., `$request.body.action`).
- Lambda integration for `$connect`, `$disconnect`, `$default`, and custom routes.
- **Management API** lets your backend push messages to specific connections by connection ID.
- Connection count and message rate matter for cost — high-concurrency / high-message-rate workloads can outgrow it.

### Common to all
- **Custom domain names** with ACM certs.
- **Stages** for deploy management.
- **Throttling** — per-stage burst and rate limits.
- **CloudWatch Logs / Metrics** — request count, 4xx/5xx, latency.
- **X-Ray tracing** — distributed tracing through API Gateway → Lambda → downstream.
- **AWS WAF** — REST API directly; HTTP API via CloudFront.
- **Mutual TLS (mTLS)** — REST API and HTTP API both support client cert validation.

## Pricing model

- **HTTP API**: per million requests + data transfer.
- **REST API**: per million requests (significantly more than HTTP API) + optional caching (per cache-size-hour) + data transfer.
- **WebSocket API**: per million messages + connection-minutes.
- **Caching (REST API only)**: per cache-size-hour (0.5 GB through 237 GB tiers).
- **VPC Link** — per-hour + per-GB processed (for private integrations).
- **No charge for the gateway being deployed** — strictly per request / per message.

The HTTP API vs REST API price gap (~71% cheaper for HTTP API) is the dominant economic lever; the per-million-requests math at typical traffic adds up to thousands per month at scale.

## Quotas & limits

- **HTTP API rate**: 10,000 RPS default per account per Region (raisable).
- **REST API rate**: 10,000 RPS default (raisable).
- **WebSocket connections**: 500,000 default per account per Region.
- **Message size (WebSocket)**: 32 KB per frame; 128 KB per message.
- **Payload size (HTTP/REST)**: 10 MB request, 10 MB response.
- **Timeout (HTTP/REST integration)**: 30 seconds (REST API hard limit); 30 seconds for HTTP API too. Lambda Function URLs (without API Gateway) can run up to Lambda's 15-minute max.
- **API routes per HTTP API**: 300.
- **Custom domain names**: 120 per account per Region.

## Common pitfalls

- **Defaulting to REST API.** Most new APIs don't need REST API's extra features. HTTP API saves 71% of the per-request cost and ~60% of latency.
- **Per-Lambda Function URL when you have many routes.** Function URLs are great for one function; API Gateway routes are much cleaner above ~3 endpoints.
- **No throttling configured.** A misbehaving client floods the API; downstream Lambda concurrency runs out; cascading failure. Set per-stage burst/rate limits and (REST API) per-method limits.
- **WAF in front of HTTP API.** HTTP API doesn't have native WAF; you need CloudFront in front. If WAF is a hard requirement, REST API is simpler.
- **30-second timeout in critical paths.** Anything that can take longer should be async (return 202, do the work in SQS / Step Functions, fetch status separately).
- **Lambda integration without warm Lambdas.** Cold start tail latency leaks to the API. Use SnapStart (Java/Python/.NET) or provisioned concurrency for latency-sensitive endpoints.
- **No request validation.** Schema validation (REST API) or model validation at the Lambda boundary; otherwise garbage requests hit your backend and cost real money to process.
- **API Gateway for internal-only east-west traffic.** Per-request charges add up; direct integration via PrivateLink / NLB / ALB is cheaper.
- **WebSocket API for chat at very high scale.** The per-connection-minute pricing scales linearly; at certain scale, custom Fargate + WebSocket server is cheaper.

## Pairs well with
- [Lambda](../compute/lambda.md) — the canonical integration target.
- [CloudFront](cloudfront.md) — in front of an API Gateway for caching + WAF (especially for HTTP API).
- **Cognito** — user pools for auth (JWT for HTTP API; authorizer for REST API).
- **Step Functions** — orchestrate behind a single API endpoint.
- **EventBridge / SQS / SNS / Kinesis** — async ingestion targets (API Gateway → service direct integration).
- **AWS WAF / Shield** — security.
- **X-Ray** — distributed tracing.

## Pairs well with these repo pages
- [Lambda](../compute/lambda.md), [CloudFront](cloudfront.md).
- `docs/04-reference-architectures/serverless-rest-api.md` (forthcoming).

## Further reading
- [Amazon API Gateway documentation](https://docs.aws.amazon.com/apigateway/).
- [Choose between REST APIs and HTTP APIs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-vs-rest.html).
- [WebSocket API overview](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-websocket-api.html).
- [JWT authorizers for HTTP API](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html).
- [API Gateway pricing](https://aws.amazon.com/api-gateway/pricing/).
