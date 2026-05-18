# EKS (Elastic Kubernetes Service)

> **One-line summary.** Managed Kubernetes control plane. You get the CNCF Kubernetes API; AWS runs the masters.

## TL;DR
- Use EKS when you specifically want the Kubernetes API — for portability, ecosystem (Argo, Helm, Operators, Istio), or because your team already runs Kubernetes elsewhere. Otherwise ECS is simpler.
- The control plane is managed; the data plane is yours (EC2 self-managed, EC2 managed node groups, Fargate, or **EKS Auto Mode** which manages nodes for you).
- **EKS Auto Mode** (launched late 2024, GA throughout 2025) is the easiest way to run EKS in 2026 — AWS manages the node lifecycle, Karpenter-style autoscaling, and core add-ons.
- IRSA (IAM Roles for Service Accounts) or the newer **Pod Identity** is how pods get AWS credentials. Never use node-level IAM for app permissions.
- The biggest hidden costs: the control plane fee per cluster ($0.10/hour ≈ $72/month — non-trivial when you run dozens), cross-AZ data transfer between pods, and ALB/NLB per Ingress.

## When to use it
- You want portable Kubernetes manifests (multi-cloud, on-prem with EKS Anywhere, hybrid with EKS Hybrid Nodes).
- You depend on the Kubernetes ecosystem — Argo CD/Workflows, Tekton, Knative, Crossplane, Istio, KEDA, operators.
- Your team has Kubernetes expertise and you want to reuse it on AWS.
- You're running ML training with Kubeflow, Ray, or similar — most ML platforms target Kubernetes first.
- You need pod-level features ECS lacks (sidecar lifecycles, ephemeral containers, init container ordering, custom schedulers).

## When NOT to use it
- You don't have a reason to run Kubernetes. ECS is simpler, cheaper at small scale (no control plane fee), and integrates as deeply with AWS.
- You're running a handful of services. The complexity tax is real — operators, networking, RBAC, version upgrades.
- You want serverless containers with no node concept — Fargate (via ECS) or App Runner-style services (now ECS Express Mode) is a better fit.

## Key concepts

**Cluster** — the Kubernetes control plane (API server, etcd, scheduler, controller-manager) managed by AWS. Highly available across 3 AZs by default. You pick the Kubernetes version; AWS supports the current and three preceding minor versions, with extended support (paid) for older versions.

**Data plane options:**
- **Managed node groups** — EC2 Auto Scaling Groups managed by EKS. AWS handles AMI updates and replacement; you choose instance types, sizes, and capacity.
- **Self-managed nodes** — bring your own ASG/launch templates. More control, more work.
- **Fargate** — serverless pods, no nodes to operate. Limited (no DaemonSets, no GPU, no privileged, slower scaling) but operationally simplest.
- **EKS Auto Mode** — AWS manages the node lifecycle entirely (instance selection, scaling via Karpenter, OS patching, node draining). Closest thing to "serverless Kubernetes" while still supporting DaemonSets, GPUs, and the rest of the K8s feature set.
- **Hybrid Nodes / EKS Anywhere / Outposts** — run the same Kubernetes outside AWS.

**Pod networking — VPC CNI.** AWS's CNI plugin gives each pod a routable VPC IP. Pod density per node is bounded by the instance's ENI/IP count. Use `prefix delegation` (default on newer setups) to pack 4× more pods per node.

**IRSA (IAM Roles for Service Accounts)** — bind a Kubernetes service account to an IAM role via OIDC federation. Pods get short-lived STS credentials. The traditional answer.

**Pod Identity** (newer) — a simpler alternative to IRSA that doesn't require an OIDC provider per cluster. Configured via the EKS Pod Identity add-on. New clusters should default to this.

**Ingress.** AWS Load Balancer Controller provisions ALBs (`Ingress`) and NLBs (`Service type=LoadBalancer`) per Kubernetes resource. Each ALB has a per-hour cost — share them via `IngressGroup` annotations across multiple Ingress objects.

**Karpenter** (AWS-built, CNCF) — the modern cluster autoscaler. Provisions nodes that exactly fit pending pods (right-sized, right-Spot-or-on-demand) instead of scaling pre-defined ASGs. Bundled into EKS Auto Mode; standalone install for managed node groups.

**Add-ons.** EKS manages the lifecycle of common add-ons (VPC CNI, CoreDNS, kube-proxy, EBS CSI driver, EFS CSI driver, Pod Identity Agent, Mountpoint for S3 CSI driver, etc.). Use managed add-ons over manual Helm installs where they exist.

## Pricing model

- **Control plane** — $0.10/hour per cluster (~$72/month). Same for standard support; **extended support** for older Kubernetes versions costs significantly more (currently $0.60/hour per cluster).
- **Data plane** — pay for the EC2 instances, Fargate tasks, or EKS Auto Mode capacity you use. Standard EC2/Fargate Savings Plans apply.
- **EKS Auto Mode** — small per-instance management fee on top of the underlying EC2 price (~12% surcharge); spares you the operational cost of Karpenter+core add-ons.
- **Data transfer** — cross-AZ pod-to-pod traffic is billed per GB. With service meshes and microservices, this adds up quickly. Use topology-aware hints (`service.kubernetes.io/topology-mode: Auto`) to prefer same-AZ.
- **ALB/NLB** — per-hour + per-LCU. Share ALBs across Ingresses via IngressGroup.

## Quotas & limits

- **Clusters per Region**: 100 by default.
- **Managed node groups per cluster**: 30.
- **Nodes per cluster** (managed/self-managed combined): documented at 1,000+ in production; very large clusters need careful etcd and API-server sizing.
- **Pods per node**: bounded by the instance's ENI count × IPs per ENI; prefix delegation increases this.
- **Fargate pods per cluster**: regional Fargate vCPU quota applies.
- **Kubernetes API server**: rate-limited; bursty controllers (Argo CD with 10k Applications) can exhaust the request budget.

## Common pitfalls

- **Running EKS for one service.** You're paying ~$72/month for the control plane before any compute. For a single service, ECS Express Mode or Fargate-via-ECS is much cheaper.
- **Not using IRSA / Pod Identity.** Giving the node role access to your S3 buckets means *every* pod on that node has that access. Always scope IAM to the workload.
- **Cross-AZ chatter without topology hints.** A service mesh + microservices easily produces multi-AZ data transfer bills bigger than the EC2 bill. Use topology-aware routing.
- **Forgetting to scale CoreDNS.** Default CoreDNS replica count doesn't scale with cluster size; DNS becomes the bottleneck on large clusters. Use NodeLocal DNSCache.
- **Long-lived clusters drift behind Kubernetes versions.** Standard support is 14 months per minor version; afterward you pay extended support fees. Plan upgrades quarterly.
- **Not pinning the Kubernetes version in IaC.** A blanket "use latest" surprises you with a major upgrade on next apply.
- **Storing secrets in plain Kubernetes Secrets.** Use Secrets Manager + the [Secrets Store CSI Driver](https://github.com/aws/secrets-store-csi-driver-provider-aws) or External Secrets Operator.
- **Cluster autoscaler with classic ASGs.** Karpenter (or EKS Auto Mode) replaces this with faster, cheaper, right-sized provisioning.

## Pairs well with
- **Karpenter / EKS Auto Mode** — modern autoscaling.
- **AWS Load Balancer Controller** — native ALB/NLB Ingress.
- **EBS / EFS / FSx CSI drivers** — persistent volumes.
- **EKS Pod Identity** — clean pod-level IAM.
- **CloudWatch Container Insights, Managed Prometheus, Managed Grafana** — observability.
- **Argo CD / Flux** — GitOps deployments.
- **App Mesh / Istio / Linkerd** — service mesh (if you actually need one).

## Pairs well with these repo pages
- [ECS](ecs.md) — the AWS-native alternative; usually the right default unless you specifically need Kubernetes.
- [Fargate](fargate.md) — the serverless data-plane option.

## Further reading
- [Amazon EKS documentation](https://docs.aws.amazon.com/eks/).
- [EKS Best Practices Guides](https://aws.github.io/aws-eks-best-practices/) (community-maintained, AWS-blessed).
- [Karpenter](https://karpenter.sh/).
- [EKS Auto Mode](https://docs.aws.amazon.com/eks/latest/userguide/automode.html).
- [Pod Identity vs IRSA](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html).
