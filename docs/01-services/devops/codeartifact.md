# CodeArtifact

> **One-line summary.** Managed artifact repository for npm, PyPI, Maven, NuGet, Ruby (RubyGems), Cargo, Swift, and generic packages. Caches public registries (npmjs, PyPI, Maven Central, NuGet Gallery) and hosts your private packages.

## TL;DR
- The right service for an AWS-native private package registry. Replaces Sonatype Nexus / JFrog Artifactory / Verdaccio for AWS-aligned teams.
- **Upstream repositories** mean you don't pay external-registry rate limits or risk supply-chain compromise of public packages — CodeArtifact mirrors what you request.
- **Domain** is the multi-account boundary; one domain can host many repositories shared across an Organization.
- IAM-authenticated; integrates with **IAM Identity Center**, **CodeBuild / CodePipeline / GitHub Actions** for credential-less pulls.
- Compared to free public registries: more expensive per-pull but eliminates rate-limit / outage risk and lets you control which packages teams can pull.

## When to use it
- Private packages for internal libraries (npm scopes, Python distributions, internal Maven artifacts).
- Caching public registries to avoid rate limits during CI scale-out (npm pull rate, Docker Hub limits, PyPI flakiness).
- Compliance-driven control over which open-source packages teams can use (block known-vulnerable packages, restrict to approved versions).
- Multi-account organizations consolidating package management.

## When NOT to use it
- Tiny teams happy with public npm / PyPI / Maven directly.
- Workloads where GitHub Packages / GitLab Package Registry fits better (because the rest of the workflow is GitHub / GitLab).
- Workloads where you'd rather run Verdaccio / Nexus / Artifactory for specific features CodeArtifact doesn't have (advanced policy, Helm repos with specific format, etc.).

## Key concepts

### Domain
Top-level resource. One domain can host many repositories, shared with member accounts in an Organization. Single KMS key per domain encrypts all repos.

### Repository
A package store within a domain. Has a set of **package formats** (npm, PyPI, Maven, NuGet, RubyGems, Cargo, Swift, generic).

### Upstream repositories
A repo can have one or more upstreams (other CodeArtifact repos or public registries). Resolution: query the repo, then fall through to upstreams. Pulls from public registries are cached locally for subsequent pulls — fast, rate-limit-free.

The canonical pattern: one **internal-only** repo for your private packages + one **proxy** repo that has the public registry as an upstream + downstream consumers point at a third **combined** repo that includes both upstreams.

### Package formats (2026)
- **npm** (Node.js).
- **PyPI** (Python).
- **Maven** (Java).
- **NuGet** (.NET).
- **RubyGems**.
- **Cargo** (Rust).
- **Swift packages**.
- **Generic** — arbitrary binary artifacts (use for things like Helm charts, CLI tarballs, etc.).

### Authentication
- **IAM-issued tokens** via `aws codeartifact get-authorization-token` — 12-hour validity by default.
- **IAM Identity Center / federated identities** supported.
- **No static credentials needed.**

### Domain / repo policies
Resource-based policies on the domain and repos for fine-grained sharing.

### Package versioning / immutability
Published versions are immutable by default (republishing the same version fails). Deletes are permitted with appropriate IAM.

### Vulnerability scanning
Integrates with **Inspector** for SBOM-style vulnerability scanning of package versions.

## Pricing model

- **Storage** — per GB-month.
- **Requests** — per 10,000 requests against the API.
- **Data transfer** — same AWS rules.

CodeArtifact pricing is typically modest unless storage volume is large.

## Quotas & limits

- **Domains per account per Region**: 10 default (raisable).
- **Repositories per domain**: 1,000.
- **Package versions per package**: high (thousands).
- **Concurrent requests**: high; AWS-managed scaling.

## Common pitfalls

- **Direct public-registry use in CI without CodeArtifact in front.** CI scale-out hits public rate limits; flakiness ensues. CodeArtifact upstream caching solves this.
- **No domain policy.** Default settings may not restrict cross-account access; explicit domain policy clarifies sharing intent.
- **Token expiration in long-running builds.** 12-hour token; for very long builds re-issue or shorten the pipeline.
- **Republishing version `1.0.0` and being surprised it fails.** Versions are immutable; bump the version.
- **One domain per team.** A single domain with many repos shared across teams (via resource policies + AWS RAM) scales better.
- **Skipping vulnerability scanning.** Inspector + CodeArtifact catches known CVEs in pulled packages.
- **Treating CodeArtifact as a free CDN for public packages.** It's not free; storage and request costs accumulate. Configure cache eviction.

## Pairs well with
- [CodeBuild](codebuild.md), [CodePipeline](codepipeline.md) — package pulls in CI.
- [Inspector](../security-identity/inspector.md) — vulnerability scanning.
- [IAM Identity Center](../security-identity/iam-identity-center.md) — federated CLI access for developers.
- [KMS](../security-identity/kms.md) — encryption at rest.
- **GitHub Actions / GitLab CI** — push / pull packages via `aws codeartifact get-authorization-token`.

## Pairs well with these repo pages
- [CodeBuild](codebuild.md), [CodePipeline](codepipeline.md), [Inspector](../security-identity/inspector.md).

## Further reading
- [AWS CodeArtifact documentation](https://docs.aws.amazon.com/codeartifact/).
- [Upstream repositories](https://docs.aws.amazon.com/codeartifact/latest/ug/repos-upstream.html).
- [Authentication / tokens](https://docs.aws.amazon.com/codeartifact/latest/ug/tokens-authentication.html).
- [Supported package formats](https://docs.aws.amazon.com/codeartifact/latest/ug/supported-package-formats.html).
- [Inspector + CodeArtifact](https://docs.aws.amazon.com/inspector/latest/user/scanning-ecr-codeartifact.html).
