# Personalize

> **One-line summary.** Managed personalization and recommendation service. Bring your own user / item / interaction data; Personalize trains and serves recommender models (user-personalization, item similarity, trending, next-best-action) without you implementing the ML.

## TL;DR
- The right service when "we have users and items and interactions and we want recommendations" but don't want to build a recommendation system from scratch.
- Built-in "recipes" cover the common recommender patterns: **user-personalization**, **similar-items**, **personalized-ranking**, **trending-now**, **next-best-action**, **personalized-actions**.
- **Real-time** event ingestion via tracker — incorporate live behavior into recommendations within seconds.
- **Filters** at query time (don't recommend out-of-stock items, exclude already-viewed, restrict to category).
- **Batch inference** for offline scoring and email / newsletter personalization.
- The data you feed it determines quality. Plan the ingest pipeline up front; minimum dataset thresholds apply for production-grade recommendations.

## When to use it
- Product recommendations on e-commerce ("recommended for you", "customers also bought").
- Content recommendations on streaming / news / education platforms.
- Personalized email / push notification content.
- Next-best-action recommendations in apps and contact centers.
- Personalized search ranking.

## When NOT to use it
- Tiny catalogs / tiny user counts — minimum dataset thresholds aren't met; cold-start dominates.
- Cases where you'd be better served by a simple "popular this week" rule — Personalize is overkill for that.
- Personalization that needs deep custom feature engineering — building a custom model on SageMaker may be the right path.
- Workloads where transparency / explainability of recommendations is a hard requirement — Personalize is an opaque model.

## Key concepts

### Dataset Group
Top-level container for related datasets.

### Datasets
Three core types:
- **Interactions** — user-item interaction events (`user_id`, `item_id`, `timestamp`, optional `event_type`).
- **Users** — user metadata (demographics, profile).
- **Items** — item metadata (category, price, attributes).

Plus optional: **Actions** (for personalized-actions / next-best-action recipes), **Action interactions**.

### Recipes
Built-in algorithms tuned for specific recommendation problems:
- **User-Personalization** — "what would this user like?" (most common).
- **Personalized-Ranking** — re-rank a user-supplied candidate list per user.
- **Similar-Items** — "users who interacted with X also interacted with…".
- **Trending-Now** — recent popularity over a sliding window.
- **Item-Affinity** — content-based similarity.
- **Personalized-Actions / Next-Best-Action** — choose the next CTA / message / offer.

### Solutions and Campaigns
- **Solution** — trained model on a Dataset Group with a chosen recipe.
- **Solution Version** — a specific trained snapshot.
- **Campaign** — real-time inference endpoint serving a Solution Version. Configure provisioned TPS for predictable latency.

### Real-time events
**Event tracker** — write live interactions to a Personalize endpoint that updates the user's recommendations within seconds.

### Filters
DSL-based filters applied at query time:
```
INCLUDE ItemID WHERE Items.CATEGORY IN ("electronics") AND Items.PRICE < 100
EXCLUDE ItemID WHERE Interactions.event_type IN ("Purchase")
```

### Batch inference
Score a large set of users offline — output to S3. Right for nightly email personalization, weekly featured-items lists.

### Recommenders (pre-built use cases)
For common e-commerce / video / retail patterns, **Domain Dataset Groups** (Domain: Retail, Video On Demand) come with pre-built recommenders — less to configure.

## Pricing model

- **Data ingestion** — per GB.
- **Training** — per training-hour (DPU-style billing during model fitting).
- **Real-time recommendations** — per TPS-hour of Campaign capacity + per recommendation served.
- **Batch inference** — per million inference requests.
- **Filters** — included.

## Quotas & limits

- **Datasets per Dataset Group**: small fixed count per dataset type.
- **Schema fields**: bounded per dataset.
- **Items / users / interactions**: practical limits in the hundreds of millions for interactions.
- **Solution Versions per Solution**: many; old versions purgeable.
- **Campaigns per Region**: bounded; raisable.
- **Filter expression complexity**: bounded.

## Common pitfalls

- **Too-little data.** Recipes have minimum dataset thresholds (often thousands of users and interactions). Below that, recommendations are essentially random.
- **No real-time event tracker.** Recommendations age quickly without new interactions feeding back. Always wire the event tracker.
- **No filters.** "Recommended out-of-stock item" / "recommend what they already bought" are common embarrassments. Use filters.
- **Single Solution Version forever.** Retraining picks up new behavior. Schedule retraining.
- **One huge Solution serving everything.** A separate Solution per use case (homepage / email / search ranking) typically performs better.
- **Skipping Domain Dataset Group when it fits.** For e-commerce / video, the domain DG is a faster start than rolling your own.
- **Treating recommendations as black-box.** Track click-through, conversion, and other downstream metrics; A/B test against simple baselines.

## Pairs well with
- [S3](../storage/s3.md) — dataset ingestion and batch inference output.
- [Kinesis](../analytics/kinesis.md), [EventBridge](../integration-messaging/eventbridge.md) — real-time event tracker upstream.
- [Lambda](../compute/lambda.md), [API Gateway](../networking/api-gateway.md) — serve recommendations to client apps.
- [DynamoDB](../database/dynamodb.md) — store recommendation output cache.
- **Amazon Pinpoint / SES** — push personalized content via email / SMS.

## Pairs well with these repo pages
- [SageMaker](sagemaker.md) — when custom modeling is required.
- [Kinesis](../analytics/kinesis.md), [EventBridge](../integration-messaging/eventbridge.md).

## Further reading
- [Amazon Personalize documentation](https://docs.aws.amazon.com/personalize/).
- [Recipes](https://docs.aws.amazon.com/personalize/latest/dg/working-with-predefined-recipes.html).
- [Domain Dataset Groups](https://docs.aws.amazon.com/personalize/latest/dg/recommenders.html).
- [Filters](https://docs.aws.amazon.com/personalize/latest/dg/filters.html).
- [Event tracker](https://docs.aws.amazon.com/personalize/latest/dg/recording-events.html).
