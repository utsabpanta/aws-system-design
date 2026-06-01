# Cloud Map

> **One-line summary.** AWS service discovery — register service instances under a friendly name, look them up via DNS or API, with optional health checks. The "service registry" primitive that other AWS services (ECS, App Mesh, EKS) integrate into.

## TL;DR

- A registry for "where is service X right now?" Maps friendly names (`orders-api.internal`) to a set of instances (containers, EC2, Lambdas, arbitrary endpoints) with metadata and health.
- Two query surfaces: **DNS** (Route 53 Private Hosted Zone under the hood) and the **DiscoverInstances API** (lower latency, returns metadata).
- The most common consumer is **ECS Service Discovery** — `aws_service_discovery_*` Terraform resources, ECS Service Connect, and the older Service Discovery integration all use Cloud Map under the hood.
- For pure service-to-service inside ECS / EKS, **ECS Service Connect** or **VPC Lattice** is usually a better starting point than rolling your own Cloud Map integration. Cloud Map is the right layer when you want a registry without committing to a specific mesh / connect product.
- Built-in health checks integrate with Route 53; unhealthy instances are filtered out of DNS responses and API queries.

## When to use it

- Service registry for mixed workloads (ECS + Lambda + on-prem + arbitrary HTTP endpoints) that need to find each other by name.
- Custom service discovery patterns that ECS Service Connect / VPC Lattice don't fit.
- Multi-account service catalog where you want a single registry shared across accounts (via Route 53 association).
- Replacement for a self-hosted Consul / etcd / Eureka without standing up the infra.

## When NOT to use it

- Pure intra-ECS service-to-service — use ECS Service Connect, which is built on Cloud Map but with a much simpler interface and automatic Envoy-based load balancing.
- Pure intra-EKS — use Kubernetes Services (CoreDNS) for in-cluster discovery; **VPC Lattice** for cross-VPC / cross-account.
- Public-facing endpoints — use Route 53 directly (Cloud Map's value is the dynamic-registry pattern, which public DNS doesn't need).

## Key concepts

**Namespace.** Top-level grouping. Three flavors:

- **Public DNS namespace** — public Route 53 hosted zone; service names are publicly resolvable. (`example.com`.)
- **Private DNS namespace** — VPC-private hosted zone; names resolve only inside the VPCs that the namespace is associated with. (`prod.internal`.)
- **HTTP namespace** — no DNS records; only the `DiscoverInstances` API. Useful when consumers don't need or want DNS.

**Service.** A logical service inside the namespace (`orders`, `users-api`). Each service has DNS settings (record type, TTL) and optionally a health-check configuration.

**Service instance.** A specific endpoint (`{ "AWS_INSTANCE_IPV4": "10.0.1.42", "AWS_INSTANCE_PORT": "8080" }`). Registered via `RegisterInstance`, deregistered via `DeregisterInstance`. ECS does this automatically when configured for Service Discovery.

**Health checks.**

- **Route 53 health check** — Route 53 polls the endpoint; unhealthy instances are filtered out of DNS responses.
- **Custom health check** — your service (or a CI / monitoring system) updates instance health via API. Cheaper for high-cardinality instance counts.

**TTL and record types.** DNS records emitted from Cloud Map have a TTL. Lower TTLs → faster failover but more DNS queries. Use the API (no caching) for very-fresh-data needs.

**Integration with ECS.** ECS service definitions can declare a `serviceDiscovery` block referencing a Cloud Map service; ECS auto-registers / -deregisters tasks as they come and go.

**Integration with ECS Service Connect.** Service Connect creates Cloud Map services for you behind the scenes; the developer experience is "set `serviceConnectConfiguration` on the ECS service," not "configure Cloud Map directly."

**Cross-account / cross-VPC sharing.** A private DNS namespace's underlying Route 53 zone can be associated with VPCs from other accounts via cross-account Route 53 association. Consumer accounts resolve the names natively.

## Pricing model

- **Per registered service instance per hour** (small).
- **Per million `DiscoverInstances` API calls**.
- **Per million DNS queries** (charged through Route 53 for DNS namespaces).
- **Route 53 health checks** — per check per month + extra for HTTPS / string match.

Cloud Map is cheap. The dominant cost is at very high cardinality (tens of thousands of instances registered) or very high query rate.

## Quotas & limits

- **Namespaces per account per Region**: 1,000.
- **Services per namespace**: 1,000.
- **Instances per service**: 1,000 (raisable).
- **DiscoverInstances rate**: high default, raisable.
- **Custom attributes per instance**: 30 attributes, 1 KB each.

## Common pitfalls

- **Reaching for Cloud Map when ECS Service Connect / VPC Lattice would be enough.** Service Connect is built on top of Cloud Map and gives you load balancing + retries + observability out of the box; Cloud Map alone gives you a registry and DNS.
- **Long TTLs on dynamic services.** A 60-second TTL means up to 60 s of stale DNS after an instance fails. Use shorter TTLs (with the trade-off of more queries) or call `DiscoverInstances` directly for sensitive paths.
- **No health checks.** Without them, DNS keeps handing out IPs for dead services. Configure either Route 53 health checks (managed polling) or custom health checks (push-based from your monitoring).
- **HTTP namespace consumers depending on DNS.** Won't work; HTTP namespace has no DNS records. Either use a DNS namespace or update consumers to call `DiscoverInstances`.
- **Cross-account private DNS unconfigured.** A consumer in another account that hasn't been associated with the private hosted zone won't resolve the names — and the error is opaque ("NXDOMAIN").
- **Treating it as the source of truth for service topology.** It's a runtime registry. Documentation, dependency graphs, and architecture diagrams need a separate home.

## Pairs well with

- [ECS](../compute/ecs.md) — primary consumer.
- [Route 53](route53.md) — private hosted zone under DNS namespaces.
- [VPC](vpc.md) — private namespaces are associated with VPCs.
- **ECS Service Connect** — the higher-level abstraction many teams should use instead.
- **AWS App Mesh** (legacy) / **VPC Lattice** — alternative service-to-service primitives.

## Pairs well with these repo pages

- [ECS](../compute/ecs.md), [EKS](../compute/eks.md).
- [App Mesh](app-mesh.md) — what to migrate away from; Cloud Map underpinned its naming.

## Further reading

- [AWS Cloud Map documentation](https://docs.aws.amazon.com/cloud-map/).
- [Cloud Map with ECS Service Discovery](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-discovery.html).
- [Cloud Map and ECS Service Connect](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect-concepts.html).
- [Cloud Map pricing](https://aws.amazon.com/cloud-map/pricing/).
