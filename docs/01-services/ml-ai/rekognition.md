# Rekognition

> **One-line summary.** Managed computer vision API. Image and video analysis — object/scene detection, content moderation, text extraction, face analysis (with strict policies), celebrity recognition, custom models.

## TL;DR
- Pre-trained vision API for images (sync) and video (async, on S3 video files or Kinesis Video Streams).
- Common uses: **content moderation** (UGC platforms), **document / image text** (`DetectText`), **object & scene labels**, **face detection / analysis** for unlock-style UX, **face comparison** for identity verification, and **custom labels** via your own training data.
- **Face features are restricted** — face-verification / face-comparison / face-search are governed by AWS's responsible-AI / Acceptable Use policy. Some use cases require additional review.
- For one-off OCR of structured documents (forms, tables, signatures), **Textract** is the better fit. Rekognition `DetectText` is for ad-hoc text in images.
- For real-time video streams, integrates with **Kinesis Video Streams**.

## When to use it
- Moderating user-uploaded photos / videos at scale.
- Cataloging media assets (objects, scenes, activities in video).
- Lightweight document text extraction.
- Identity verification flows (face match against a stored reference).
- Custom image classification (train **Custom Labels** on your own dataset).

## When NOT to use it
- Structured document understanding (forms, tables, key-value pairs) — use **Textract**.
- Generic generative-vision tasks (caption images with rich natural language, answer questions about images) — use a vision-capable LLM on **Bedrock**.
- Workloads where face features are required but Acceptable Use review hasn't been completed.

## Key concepts

### APIs

**Images:**
- `DetectLabels` — objects, scenes, activities, with confidence scores.
- `DetectModerationLabels` — content moderation taxonomy (explicit, suggestive, violence, etc.).
- `DetectText` — text in images (signs, banners, screenshots).
- `DetectFaces` / `CompareFaces` / `IndexFaces` / `SearchFaces` — face analysis (restricted).
- `RecognizeCelebrities` — celebrities (restricted use cases).
- `DetectProtectiveEquipment` — PPE detection.

**Video (async, S3-based or Kinesis Video Streams):**
- Same categories: labels, moderation, faces, persons (tracking), shots, segments.
- Async pattern: start a job, get notified via SNS when done, retrieve results.

**Custom Labels.** Train your own image classifier or object detector on a small dataset. Managed training and inference. AWS auto-scales the inference endpoint.

**Streaming Video.** Real-time inference on Kinesis Video Streams — e.g., person-tracking in security cameras.

**Face Liveness.** Detects whether the face presented to the camera is from a live person (vs photo, video replay, mask). Used in onboarding flows.

### Restricted use
AWS's face-related APIs are restricted by Acceptable Use policy — particularly around use by law enforcement and unconstrained surveillance. Some use cases require pre-approval; new accounts have additional onboarding steps for face features.

## Pricing model

- **Per image processed** for each API.
- **Per minute of video processed** for video APIs.
- **Custom Labels** — per inference hour while the trained endpoint is active + per training hour.
- **Face storage** for `IndexFaces` collections — per face per month.

Pricing scales linearly with volume; bulk pricing tiers reduce per-unit cost at high volumes.

## Quotas & limits

- **Image size**: 5 MB direct upload, 15 MB via S3.
- **Video size**: 10 GB; up to 6 hours per video.
- **Custom Labels** datasets: limited (configure per project).
- **Concurrent video jobs**: bounded per account; raisable.
- **Face Collections per Region**: thousands; faces per collection: up to ~20 million.

## Common pitfalls

- **Using `DetectText` for structured forms.** Rekognition reads text; **Textract** understands structure.
- **No moderation pipeline.** A UGC platform without automated moderation accumulates harmful content fast. Wire `DetectModerationLabels` into the upload path.
- **Custom Labels models with too little data.** Few-shot custom training has a floor; expect to provide hundreds-to-thousands of images per class for good accuracy.
- **Face APIs deployed without an AUP review.** Restricted-use features can be blocked or revoked; plan around the policy.
- **Per-frame video inference on long files.** Use video APIs (which sample frames intelligently); calling image APIs frame-by-frame is expensive and slower.
- **Storing face IDs without lifecycle.** Indexed faces persist until deleted; for ephemeral verification, delete after use.

## Pairs well with
- [S3](../storage/s3.md) — image / video storage.
- [Kinesis Video Streams](../analytics/kinesis.md) — real-time video.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — orchestrate moderation pipelines.
- [Textract](textract.md) — structured document understanding.
- [Bedrock](bedrock.md) — vision-capable LLMs for richer captioning / VQA.

## Pairs well with these repo pages
- [Textract](textract.md), [Bedrock](bedrock.md), [SageMaker](sagemaker.md).

## Further reading
- [Amazon Rekognition documentation](https://docs.aws.amazon.com/rekognition/).
- [Custom Labels](https://docs.aws.amazon.com/rekognition/latest/customlabels-dg/what-is.html).
- [Face Liveness](https://docs.aws.amazon.com/rekognition/latest/dg/face-liveness.html).
- [Acceptable Use Policy (AWS)](https://aws.amazon.com/aup/).
- [Rekognition Video stream processors](https://docs.aws.amazon.com/rekognition/latest/dg/streaming-video.html).
