# SageMaker

> **One-line summary.** AWS's end-to-end ML platform — managed training, inference, notebooks, pipelines, feature store, model registry, labeling, MLOps, and (in 2024-2026) the unified data + AI **SageMaker Unified Studio** experience.

## TL;DR

- SageMaker is a large umbrella. Its primary "do ML here" tier was renamed **Amazon SageMaker AI**; the broader brand "Amazon SageMaker" now also covers data engineering, governance, and the **Unified Studio** IDE that ties everything together.
- **SageMaker Studio Classic is no longer available for new onboarding**. New users get the **Unified Studio** experience; existing Studio Classic environments continue but can only be stopped / deleted, not freshly created.
- The right "I want to do ML on AWS" service when **Bedrock** doesn't fit — i.e., custom models, classical ML, large-scale training, ML pipelines beyond LLM serving.
- Sub-products that matter: **Training** (managed jobs on managed clusters), **Inference** (real-time endpoints, async endpoints, batch transform, serverless inference), **Pipelines** (ML CI/CD), **Feature Store**, **Model Registry**, **Ground Truth** (labeling), **Canvas** (no-code), **JumpStart** (model hub), **HyperPod** (large-scale training clusters).
- Pricing is mostly per instance-hour for training and inference, with serverless / async modes for spiky workloads. The biggest cost mistake is over-provisioned real-time endpoints sitting idle.

## When to use it

- Custom model training (deep learning, classical ML) with managed clusters.
- Production inference (real-time, async, batch, serverless) at scale.
- ML pipelines with reproducible training/eval/deploy/monitor stages.
- Data labeling with Ground Truth.
- Large-scale distributed training (HyperPod for thousands-of-accelerator runs).
- Low-code / no-code ML for analysts (Canvas, including time-series forecasting).
- Multi-team ML platforms with governance, lineage, and the Unified Studio collaborative workspace.

## When NOT to use it

- LLM applications where you want pre-built foundation models accessible by API — use **Bedrock**.
- Specific AI tasks AWS already has a managed service for (OCR → Textract, transcription → Transcribe, translation → Translate, image labeling → Rekognition, etc.).
- Tiny ML workloads where running a managed cluster is overkill — sometimes a Lambda + scikit-learn pickled model is enough.

## Key concepts

### SageMaker Unified Studio

The new IDE experience. One workspace combining:

- **Notebooks** (JupyterLab, Code Editor, multiple code spaces per project).
- **SageMaker AI** for model training / inference / pipelines.
- **Data Engineering** integrations with Glue, EMR, Athena, Redshift.
- **Lake Formation** for governance.
- **Catalog + lineage** across data and models.

Recent (2026) features: notebook import / export, cell reordering, multiple per-project code spaces, multi-line SQL support, **CI/CD CLI** (`aws-smus-cicd-cli`) for multi-environment deployments.

### SageMaker Studio Classic (legacy)

The original JupyterLab-based IDE. **No new onboarding** — only existing customers can keep using it. AWS recommends migrating to Unified Studio.

### Training

- **Training Jobs** — submit a job; SageMaker provisions instances, runs your training script, saves the artifact to S3, tears down.
- **Built-in algorithms** — XGBoost, Linear Learner, K-Means, etc. Use your own framework (PyTorch, TensorFlow, Hugging Face) via managed images.
- **Spot training** — up to 90% off for fault-tolerant training jobs.
- **Distributed training libraries** — SageMaker's distributed data parallel (SMDDP) and model parallel (SMP) for large models.
- **Warm pools** — keep training instances warm between jobs to skip provisioning latency.

### Inference (four modes)

- **Real-time endpoint** — always-on, low-latency. Auto-scaling supported. Right for steady prediction traffic.
- **Serverless inference** — no instance to manage; pay per invocation + duration. Right for spiky / unknown traffic.
- **Asynchronous inference** — long-running predictions (up to 60 minutes), queue-based, large payloads.
- **Batch transform** — offline scoring of large datasets to S3.

**Multi-model endpoints** and **multi-container endpoints** let one instance host many models (or pipelines of models) to amortize cost.

### Pipelines

SageMaker Pipelines define multi-step ML workflows (data prep → training → eval → deploy) as a DAG. Versioned, parameterized, integrates with Step Functions for broader orchestration.

### Feature Store

Online (low-latency lookup) + offline (S3 / Iceberg) feature storage. Time-travel reads for point-in-time correct training data.

### Model Registry

Versioned model artifacts with approval workflows. The MLOps gate between training and production deployment.

### Ground Truth

Managed data labeling. Human workforces (your team, Mechanical Turk, vendors), built-in labeling UIs (bounding boxes, image classification, text classification, named entity).

### Canvas

No-code ML for business analysts. Time-series forecasting, classification, regression, text classification, image classification. Replacement target for **Amazon Forecast** (which is closed to new customers).

### JumpStart

Model hub — pre-trained foundation models, open-source LLMs, vision models — one-click deploy as SageMaker endpoints. Includes Llama, Mistral, Falcon, Stable Diffusion, BERT, etc.

### HyperPod

Resilient, large-scale training clusters for foundation-model training. Handles instance failures, automatic recovery, cluster lifecycle for multi-week training runs.

### MLOps + Governance

Model Cards (model documentation), Model Monitor (drift detection), Clarify (bias and explainability), Pipelines for reproducibility, ML lineage tracking.

## Pricing model

- **Notebook / Studio instances** — per-instance-hour for the IDE host.
- **Training jobs** — per-instance-hour by class (CPU, GPU, accelerators); Spot 60-90% off.
- **Real-time inference** — per-instance-hour for the endpoint.
- **Serverless inference** — per million invocations + per GB-second duration.
- **Async inference** — instance-hours only while jobs run.
- **Batch transform** — per-instance-hour while jobs run.
- **Pipelines / Feature Store / Model Registry / Ground Truth / Canvas** — separate dimensions; Ground Truth charges per labeled object + workforce cost.

The biggest cost mistake: **leaving real-time endpoints up at production-class sizing for low-traffic models.** Use serverless or async inference for those.

## Quotas & limits

- **Concurrent training jobs**: high (raisable).
- **Endpoints per account per Region**: 100s, raisable.
- **Endpoint variants and shadow tests**: bounded; check current docs.
- **Multi-model endpoint model count**: thousands.
- **Pipeline definition size**: large, with parameterization.
- **HyperPod cluster size**: very large (hundreds-thousands of accelerators).

## Common pitfalls

- **Real-time endpoint for occasional inference.** Serverless or async fits better and avoids 24/7 idle cost.
- **Re-onboarding to Studio Classic.** Not possible for new users; go straight to Unified Studio.
- **Training without Spot.** Most training jobs tolerate Spot interruption (with checkpointing); 60-90% savings.
- **No Model Registry between training and prod.** Untracked model promotions are an audit nightmare. Use Model Registry + approval workflows.
- **One feature group per use case without an offline strategy.** Online Feature Store is fast but expensive; offline (S3/Iceberg) is for training-data backfill. Use both intentionally.
- **Pipelines used only for happy-path.** Wire failure handling, alerts, and retries; otherwise broken pipelines silently produce stale models.
- **No SageMaker Model Monitor.** Drift, data quality, and bias problems show up first in production. Monitor at the endpoint.
- **Forecast users not migrating.** Forecast is closed to new customers since July 2024; existing customers should plan migration to SageMaker Canvas.
- **HyperPod treated as the default for any GPU training.** It's for very large, long-running, resilience-critical runs. Smaller jobs run fine on regular Training Jobs.

## Pairs well with

- [Bedrock](bedrock.md) — for the LLM-as-API path; complementary to SageMaker custom-model work.
- [S3](../storage/s3.md) — training data, model artifacts, batch transform input/output.
- [Glue](../analytics/glue.md), [Lake Formation](../analytics/lake-formation.md) — data engineering inputs.
- [Step Functions](../integration-messaging/step-functions.md), [EventBridge](../integration-messaging/eventbridge.md) — broader orchestration.
- [Kinesis](../analytics/kinesis.md), [MSK](../analytics/msk.md) — streaming feature inputs.
- **AWS HealthLake / Comprehend Medical** — healthcare-specific pipelines.

## Pairs well with these repo pages

- [Bedrock](bedrock.md) for LLM workloads, [Forecast](forecast.md) (migration), [Athena](../analytics/athena.md), [Glue](../analytics/glue.md).
- `docs/04-reference-architectures/ml-training-inference.md` (forthcoming).

## Further reading

- [Amazon SageMaker documentation](https://docs.aws.amazon.com/sagemaker/).
- [SageMaker Unified Studio](https://aws.amazon.com/sagemaker/unified-studio/).
- [Migrating from Studio Classic](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-migrate.html).
- [SageMaker Inference options](https://docs.aws.amazon.com/sagemaker/latest/dg/deploy-model.html).
- [HyperPod](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-hyperpod.html).
- [SageMaker Canvas](https://docs.aws.amazon.com/sagemaker/latest/dg/canvas.html).
