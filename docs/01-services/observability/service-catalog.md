# Service Catalog

> **One-line summary.** Curated catalog of AWS resources — admins package CloudFormation templates as "products" in "portfolios"; end users provision them as governed, IAM-scoped self-service.

## TL;DR

- Lets a platform / cloud-center-of-excellence team **publish vetted infrastructure patterns** that developers can self-service-provision without learning CloudFormation or having broad IAM.
- **Products** wrap a CloudFormation (or Terraform Cloud / Open Source) template; **portfolios** group products and define access (who can see / launch what).
- **Constraints** restrict how a product is launched: launch role (the IAM role used), allowed parameter values, notification targets, tags, account-level resource limits.
- Underpins **Account Factory Customization (AFC)** in Control Tower — blueprints that bootstrap new accounts.
- Most-used in regulated / large enterprises that need governed self-service; less common in small fast-moving teams that just use CDK / Terraform directly.

## When to use it

- Platform / Cloud Center of Excellence (CCoE) teams publishing approved patterns (VPC, EKS cluster, RDS database, S3 bucket with the right defaults).
- Compliance environments where developers need provisioning power without broad IAM.
- Multi-team self-service — give product teams a portfolio of "the things you're allowed to create."
- Control Tower Account Factory Customization.

## When NOT to use it

- Small teams comfortable with direct CDK / CloudFormation / Terraform.
- Workloads where the catalog overhead exceeds the governance benefit.
- Teams using a third-party developer platform (Backstage, Port) with its own pattern library.

## Key concepts

### Portfolios

Collection of products + a list of principals (IAM users, roles, groups) that can use it. Constraints applied at the portfolio or product level.

### Products

- **CloudFormation product** — wraps a CFN template (versioned).
- **Terraform Cloud product** — wraps a Terraform Cloud workspace.
- **Terraform Open Source product** — wraps a Terraform configuration with a managed runner.
- **External product** — generic external provisioning workflow.

### Versions

Each product is versioned. Users see the available versions; admins can deprecate old versions, mark a default.

### Constraints

- **Launch constraint** — IAM role used to provision. Lets developers launch without owning the IAM permissions themselves.
- **Template constraint** — restrict allowed values for parameters (whitelist of instance types, regions).
- **Notification constraint** — SNS notification on stack events.
- **Tag option** — required tags + allowed values.
- **Stack-set constraint** — provision across multiple accounts / Regions.
- **Resource update constraint** — restrict updates to certain resources.

### Provisioning

End user opens Service Catalog, picks a product, fills parameters, clicks **Launch**. CloudFormation creates the resources under the launch role's IAM — user doesn't need direct IAM.

### Sharing across accounts

- **Local portfolios** — same-account use.
- **Shared portfolios** — share with other accounts (org-wide or specific) via AWS Organizations integration; recipients can import to their own portfolios.

### TagOptions

Library of tags applied to provisioned resources for consistency.

### Service Catalog AppRegistry

A catalog of *applications* (not just products). Groups resources across services (CloudFormation stacks, ECS services, Lambda functions) into a logical application — pairs with Systems Manager Application Manager.

## Pricing model

- **Service Catalog itself is free.**
- You pay for the underlying resources the products provision.
- **Provisioned product launches per month**: small per-launch fee on Hub-and-Spoke (sharing) accounts.
- **Terraform Cloud / Open Source products**: per-engine pricing for the Terraform runner.

## Quotas & limits

- **Portfolios per account per Region**: 100 default.
- **Products per portfolio**: 100 default.
- **Versions per product**: 50.
- **Provisioned products per account per Region**: 1,000.
- **Constraints per product per portfolio**: bounded; check current docs.

## Common pitfalls

- **Catalog without curated products.** Empty portfolios = no value. Start with the 5-10 most-requested patterns; expand based on use.
- **No launch constraint.** Without a launch role, users need direct IAM to launch — defeats the governance value.
- **Versions never deprecated.** Old versions accumulate; users pick the latest random version. Mark a default and deprecate aggressively.
- **Manual provisioning bypassing Service Catalog.** "Devs go around it" is the failure mode. Pair Service Catalog with SCPs that block direct provisioning of the same resources.
- **Tag options skipped.** Without consistent tagging, cost attribution and resource lifecycle suffer.
- **No Terraform path for Terraform-shop teams.** Forcing CloudFormation when the team is Terraform-fluent gets resistance. Use the Terraform product types.
- **No telemetry on portfolio usage.** Which products are used / unused? Without metrics, the catalog stagnates.

## Pairs well with

- [Control Tower](control-tower.md) — Account Factory Customization uses Service Catalog blueprints.
- [Organizations](organizations.md) — cross-account portfolio sharing.
- [CloudFormation](../devops/cloudformation.md) — product template format.
- **Terraform Cloud / OSS** — alternative product format.
- [Systems Manager Application Manager](systems-manager.md) — pairs with AppRegistry for application-level operations.

## Pairs well with these repo pages

- [Control Tower](control-tower.md), [Organizations](organizations.md), [CloudFormation](../devops/cloudformation.md).

## Further reading

- [AWS Service Catalog documentation](https://docs.aws.amazon.com/servicecatalog/).
- [Portfolios](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/catalogs_portfolios.html).
- [Launch constraints](https://docs.aws.amazon.com/servicecatalog/latest/adminguide/constraints-launch.html).
- [Service Catalog AppRegistry](https://docs.aws.amazon.com/servicecatalog/latest/arguide/intro-app-registry.html).
- [Account Factory Customization with Service Catalog](https://aws.amazon.com/blogs/mt/automate-account-customization-using-account-factory-customization-in-aws-control-tower/).
