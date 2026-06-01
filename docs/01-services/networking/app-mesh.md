# App Mesh

> **One-line summary.** AWS-managed service mesh built on Envoy proxies. **Being shut down on September 30, 2026.**

## Status

> 🛑 **AWS App Mesh is being discontinued.**
>
> - **Closed to new customers since September 24, 2024.**
> - **End of service: September 30, 2026.** AWS will stop providing critical security and availability updates after that date.
> - Until end of service, existing customers can keep using App Mesh (including creating new resources and onboarding new accounts via CLI/CFN).
>
> **AWS-recommended migration targets:**
>
> - **EKS workloads** → **Amazon VPC Lattice** — eliminates sidecar proxies; managed control + data plane; cross-account / cross-VPC support via AWS RAM.
> - **ECS workloads** → **Amazon ECS Service Connect** (the AWS-native alternative for ECS service mesh-style features).
>
> This page exists for existing users and migration reference. If you're starting fresh, jump straight to VPC Lattice or ECS Service Connect.

## TL;DR

- App Mesh provided service-to-service traffic management — routing rules, retries, circuit breakers, observability — on top of Envoy sidecar proxies running in your ECS / EKS / EC2 workloads.
- The model: a managed control plane (Envoy xDS server) pushes config to sidecars; the sidecars handle every request and report metrics / traces.
- Worked well in production for years; AWS shipped two natively-integrated alternatives (Service Connect for ECS, VPC Lattice for EKS / multi-account) and is sunsetting App Mesh.
- The big migration question is **VPC Lattice vs ECS Service Connect** — pick by your compute platform and whether cross-account access is required.

## When to use it

- You already use App Mesh; you have until September 30, 2026 to migrate.

## When NOT to use it

- Any new project — use VPC Lattice or ECS Service Connect.

## Key concepts (for existing users)

**Mesh.** The top-level boundary. Multiple meshes can exist in one account, typically per environment or per organization.

**Virtual node.** Logical representation of a service / version in the mesh. Maps to one or more ECS tasks / EKS pods / EC2 instances running an Envoy sidecar.

**Virtual service.** A logical service name (`orders.internal`) that other services call. Routes to one or more virtual nodes.

**Virtual router and routes.** Traffic policies — weighted routing across virtual nodes (canary), HTTP path matching, retries, timeouts.

**Virtual gateway.** Ingress for traffic from outside the mesh.

**Sidecar (Envoy).** Container running alongside your app, intercepting traffic via iptables redirection (in ECS) or CNI rules (in EKS). Configured from the App Mesh control plane.

**Observability.** Sidecar emits Prometheus-style metrics, OpenTelemetry traces, structured access logs.

## Migration paths

### EKS → VPC Lattice

- **No more sidecars.** VPC Lattice is a managed data plane; pods talk directly to the Lattice service network.
- **Cross-account / cross-VPC by design** — services published to a Lattice service network can be consumed from other accounts via AWS RAM, without VPC peering or PrivateLink endpoints.
- **AWS Gateway API Controller** for EKS — define Lattice routes as Kubernetes `Gateway` / `HTTPRoute` resources.
- AWS migration guidance: [Migrating from AWS App Mesh to Amazon VPC Lattice](https://aws.amazon.com/blogs/containers/migrating-from-aws-app-mesh-to-amazon-vpc-lattice/).

### ECS → ECS Service Connect

- **Service Connect** is built into ECS; configured per service.
- Envoy-based, but the proxy is **managed by ECS itself** (not a sidecar you maintain).
- Service discovery via DNS, health-aware client-side load balancing, automatic retries, native CloudWatch metrics.
- Cleaner than App Mesh in the ECS-only world; less powerful than VPC Lattice for cross-account.
- AWS migration guidance: [Migrating from AWS App Mesh to Amazon ECS Service Connect](https://aws.amazon.com/blogs/containers/migrating-from-aws-app-mesh-to-amazon-ecs-service-connect/).

### Choosing between them

| Need | Pick |
|---|---|
| Pure ECS, no cross-account | **ECS Service Connect** |
| EKS / Kubernetes-style policy | **VPC Lattice** (with AWS Gateway API Controller) |
| Cross-account service publishing | **VPC Lattice** |
| Already standardized on open-source Envoy or Istio | Stay on Envoy/Istio in EKS rather than VPC Lattice |
| Multi-runtime (ECS + EKS + EC2) shared mesh | **VPC Lattice** is the broadest fit |

## Pricing model (App Mesh, for completeness)

- App Mesh the service was free. You paid for the underlying compute / data transfer.
- VPC Lattice has its own pricing (per-Lattice-service, per-request, per-GB processed).
- ECS Service Connect is included in ECS — no extra service fee.

## Common pitfalls

- **Treating the migration as urgent only after September 2026.** New features and integrations have already moved to Lattice / Service Connect. Migrating sooner means less drift.
- **Lift-and-shift to VPC Lattice without rethinking sidecar dependencies.** Sidecar-based features (custom Envoy filters, in-mesh mTLS with specific cipher suites) may need different implementations. Audit your Envoy config before migration.
- **Forgetting cross-account use cases.** If App Mesh wasn't doing cross-account for you and ECS Service Connect is enough, take Service Connect. If you do need cross-account, plan for VPC Lattice.
- **Migrating one service at a time without a coexistence plan.** Some services on App Mesh, some on Service Connect / Lattice — services need to reach each other during the migration window. Test the boundary traffic patterns explicitly.

## Pairs well with these repo pages

- [ECS](../compute/ecs.md) — host of ECS Service Connect.
- [EKS](../compute/eks.md) — host of VPC Lattice consumers via Gateway API Controller.
- [PrivateLink](vpc-endpoints.md) — adjacent cross-account / cross-VPC primitive.

## Further reading

- [App Mesh discontinuation announcement](https://aws.amazon.com/blogs/containers/migrating-from-aws-app-mesh-to-amazon-vpc-lattice/).
- [Amazon VPC Lattice documentation](https://docs.aws.amazon.com/vpc-lattice/).
- [Amazon ECS Service Connect](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-connect.html).
- [Migrate ECS workloads from App Mesh to VPC Lattice](https://aws.amazon.com/blogs/containers/migrate-amazon-ecs-workloads-from-aws-app-mesh-to-amazon-vpc-lattice/).
- [AWS App Mesh documentation](https://docs.aws.amazon.com/app-mesh/) (legacy, for existing customers).
