# SWF (Simple Workflow Service)

> **One-line summary.** AWS's original workflow orchestration service. **Legacy** — supported but not actively developed. **Step Functions is the recommended choice for new workloads.**

## Status

> ⚠️ **SWF is in maintenance mode.** Not officially deprecated, but AWS has not shipped notable upgrades in years and openly recommends Step Functions for new applications. AWS continues to operate the service for existing customers.
>
> **New workloads should use [Step Functions](step-functions.md)** — it's the actively-developed AWS workflow service, with better integrations, lower operational overhead, and a cleaner mental model.
>
> This page exists for existing SWF users and to document the migration consideration.

## TL;DR
- SWF launched in 2012 as AWS's first orchestration service. State machines defined imperatively in code via the **AWS Flow Framework** (Java; Ruby support discontinued).
- Workflow worker (your code) polls SWF for decisions to make; activity workers poll for activities to execute. AWS hosts the state; you host the workers.
- Compared to Step Functions: more flexibility (you can write any orchestration logic in code), much more operational overhead (you run the workers), and no AWS-native service integrations.
- **Modern workloads should use Step Functions** — Standard or Express workflows cover essentially every SWF use case with less code and less infrastructure.
- The narrow remaining case for SWF: existing apps where rewriting the workflow logic into Step Functions ASL isn't yet worth it, or workflows that fundamentally need the imperative model SWF provides.

## When to use it
- You already use SWF; you're not yet ready to migrate.
- **For new workloads: don't.** Use [Step Functions](step-functions.md).

## When NOT to use it
- Any new workload — Step Functions is the better answer.
- Even most existing workloads — the migration to Step Functions is usually worth doing within a year or two.

## Key concepts (for existing users)

**Domain.** Top-level namespace.

**Workflow Type.** A versioned workflow definition.

**Activity Type.** A versioned activity (the unit of work the workflow coordinates).

**Workflow Execution.** A specific instance of a workflow running.

**Decider.** The workflow worker — polls SWF for decision tasks, evaluates "what should this workflow do next," and tells SWF the next action (schedule activity, start child workflow, complete, fail).

**Activity Worker.** The activity-execution worker — polls for activity tasks, executes the work, reports completion / failure.

**History.** SWF retains the full event history per workflow execution; the decider uses this to compute the next decision.

**Flow Framework.** The (Java) library that abstracts the decider polling loop. Lets you write workflows in idiomatic Java with promises and async/await-like semantics. (Ruby framework discontinued; PHP / Python community libraries exist but unmaintained.)

## Migration to Step Functions

A practical migration approach:

1. **Inventory** workflows by complexity and traffic. Start with the simplest / lowest-stakes.
2. **Map workflow logic to ASL.** Most SWF deciders translate to Step Functions state machines — Tasks become Lambda / SDK / ECS invocations; Choice maps to Choice states; Parallel branches map to Parallel; Activities to Task states.
3. **For workflows that depend on heavy decider logic:** consider Step Functions **Express** workflows with Lambda for decision logic, or refactor the decisions into the workflow itself.
4. **Use Step Functions Workflow Studio** for visual prototyping.
5. **Run side-by-side** during cutover — leave SWF running for in-flight workflows; route new starts to Step Functions; let SWF drain.
6. **Decommission** when in-flight executions complete.

The migration usually finds simplifications — workflow logic that was buried in the decider becomes explicit in the state machine.

## Pricing model

- **Per workflow / activity / decision task** scheduled.
- **Per workflow execution** retained for the history window.
- **Per signal sent / received**.

SWF pricing is generally cheaper per-transition than Step Functions Standard for very high-volume workflows, but the operational cost of running decider / activity worker fleets usually outweighs the per-transition saving.

## Quotas & limits

- **Workflow types / activity types per domain**: many thousands (versioned).
- **Workflow execution lifetime**: up to 1 year.
- **History size per execution**: 25,000 events.
- **Task list polling rate**: bounded by SWF API quotas.

## Common pitfalls (for existing users)

- **No migration plan.** SWF works today but innovation is happening on Step Functions. Plan the move; don't drift indefinitely.
- **Decider worker fleet sizing.** Workers must poll SWF; under-sized fleets create decision-task backlog. Over-sized fleets idle. Step Functions removes this entire concern.
- **Activity polling latency.** Long-polling activity tasks adds latency; Step Functions task invocations are managed by AWS.
- **Flow Framework version drift.** Ruby support discontinued; Java framework receives little update. Java apps may need targeted maintenance.
- **No good visualization.** The SWF console is bare; Step Functions Workflow Studio is a dramatic upgrade.
- **Multi-Region / multi-account.** SWF is Regional and lacks Step Functions' cross-account features.

## Pairs well with these repo pages
- [Step Functions](step-functions.md) — the recommended successor.
- [Lambda](../compute/lambda.md), [ECS](../compute/ecs.md) — workflow workers; even more relevant in Step Functions.

## Further reading
- [Amazon SWF documentation](https://docs.aws.amazon.com/amazonswf/).
- [Choosing between Step Functions and SWF (AWS recommendation)](https://aws.amazon.com/step-functions/faqs/).
- [Migrating from SWF to Step Functions (AWS blog patterns)](https://aws.amazon.com/blogs/compute/category/application-services/aws-step-functions/).
- [AWS Step Functions documentation](https://docs.aws.amazon.com/step-functions/).
