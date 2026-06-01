# Inspector

> **One-line summary.** Continuous vulnerability scanning for EC2 instances, ECR container images, and Lambda functions. Catches CVEs and unintended network exposure.

## TL;DR

- **Inspector v2** (the current service) is agentless for EC2 (uses SSM), event-driven for ECR images, and continuous for Lambda. No need to manage your own scanner fleet.
- Findings prioritized with **Inspector Score** (severity adjusted for environment context — e.g., a CVE that can be reached from the internet is scored higher).
- Findings flow into **Security Hub CSPM** and **EventBridge** for routing.
- **CIS benchmark scans** for EC2 (host-level hardening checks) and SBOM export are first-class features.
- Right default for any AWS account running EC2 / ECR / Lambda — like GuardDuty, the cost-to-value ratio is excellent.

## When to use it

- EC2 fleets — continuous CVE scanning of installed packages.
- ECR — scan images on push (or continuously); fail builds on critical CVEs.
- Lambda — function code + dependency scanning.
- Compliance (PCI, HIPAA, FedRAMP) that requires documented vulnerability management.

## When NOT to use it

- Non-AWS workloads — Inspector only covers EC2 / ECR / Lambda. On-prem / other-cloud needs different tools.
- Workloads requiring runtime exploit detection (active intrusion in the live container) — that's **GuardDuty EKS Runtime Monitoring** or third-party EDR.

## Key concepts

### EC2 scanning

- **Agentless** (default) — uses Systems Manager agent (already on most EC2 images) to enumerate installed packages.
- Scans for CVEs against installed packages and kernel versions.
- **Deep inspection** mode adds code library dependency scanning for application files on the instance.
- **CIS benchmark scans** — apply CIS hardening checks; map failed checks to specific guidance.

### ECR scanning

- **Enhanced scanning** (Inspector-powered) — continuous scanning of pushed images; updates findings when new CVEs surface for the image's packages even without pushing again.
- **Basic scanning** (legacy ECR feature) — scan-on-push; less comprehensive. Migrate to Enhanced.

### Lambda scanning

- Scans function code and dependency layers for CVEs.
- Triggered on function deployment + continuously as new CVEs are published.

### Findings

- **Severity** — Critical, High, Medium, Low.
- **Inspector Score** — adjusted severity that factors in **network reachability** (is this CVE on a port reachable from the internet?), **exploit availability** (is there a known exploit in the wild?), and the package's role.
- **Recommendation** — usually "upgrade package X to version Y."

### SBOM export

- Export Software Bill of Materials per image / function in CycloneDX or SPDX format. Required by some compliance regimes; useful for cross-tool integration.

### Integrations

- **Security Hub CSPM** — finding aggregation.
- **EventBridge** — automation hooks.
- **CI/CD** — fail builds via ECR scanning + EventBridge rule + CodeBuild step that blocks promotion.

## Pricing model

- **Per EC2 instance per month**.
- **Per Lambda function per month** (or per scan, depending on tier).
- **Per container image scanned** + per scan-time.
- **Deep inspection (EC2)** adds a small per-instance fee.
- **CIS benchmark scans** are charged separately.

Inspector is cheap per resource; the cost scales with fleet size. Always-on for production.

## Quotas & limits

- **Members per delegated admin**: thousands.
- **Scans per ECR repo**: high; continuous scans roll automatically.
- **Concurrent scans**: high.
- **Findings retention**: AWS retains findings until remediated or suppressed.

## Common pitfalls

- **Not enabled.** Skipping Inspector means CVEs accumulate silently. Turn it on.
- **No CI/CD gating on critical CVE findings.** A Critical CVE in a pushed image should block promotion to prod. Wire EventBridge → CodePipeline approval step or similar.
- **Suppression as the default.** Suppressing instead of patching leaves the risk. Patch first; suppress with documented reason (e.g., "no exploitable code path") only when patching is genuinely impossible.
- **Basic ECR scanning when Enhanced is available.** Enhanced is much better; basic is legacy.
- **Ignoring Lambda findings.** Lambda functions tend to accumulate stale dependencies. The Inspector + Lambda Power Tuning + dependency-update bot combination keeps them clean.
- **Findings without an owner.** Tag resources so Inspector findings route to the right team. Without ownership, findings stagnate.
- **No deep inspection on EC2 with many app libraries.** The default scans installed OS packages; app-level libs need deep inspection or a separate SCA tool.

## Pairs well with

- **Security Hub CSPM** — central aggregation.
- **EventBridge** — finding-driven automation (block deploy, page on-call).
- **Patch Manager (Systems Manager)** — apply patches based on Inspector findings.
- **CI/CD pipelines** — gate promotion on scan results.
- **ECR + CodeBuild** — image-level scanning in the pipeline.

## Pairs well with these repo pages

- [GuardDuty](guardduty.md), [Security Hub CSPM](security-hub.md).
- [Operational Excellence pillar](../../05-well-architected/operational-excellence.md).

## Further reading

- [Amazon Inspector documentation](https://docs.aws.amazon.com/inspector/).
- [Inspector for EC2](https://docs.aws.amazon.com/inspector/latest/user/scanning-ec2.html).
- [Inspector for ECR](https://docs.aws.amazon.com/inspector/latest/user/scanning-ecr.html).
- [Inspector for Lambda](https://docs.aws.amazon.com/inspector/latest/user/scanning-lambda.html).
- [SBOM export](https://docs.aws.amazon.com/inspector/latest/user/sbom-export.html).
