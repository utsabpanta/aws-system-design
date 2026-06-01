# Forecast

> **One-line summary.** AWS's managed time-series forecasting service. **Closed to new customers since July 29, 2024.** Existing customers continue; AWS recommends migrating to **Amazon SageMaker Canvas** for time-series forecasting going forward.

## Status

> ⚠️ **Amazon Forecast is closed to new customers.**
>
> - **No new customer onboarding since July 29, 2024.**
> - Existing customers can continue to use the service as normal.
> - AWS recommends migrating time-series forecasting workloads to **Amazon SageMaker Canvas**, which reportedly delivers ~50% faster model building and ~45% faster predictions than Forecast across benchmark datasets, plus more cost-effective inference (SageMaker compute pricing).
>
> This page documents Forecast for existing users and migration reference. **For new forecasting workloads, jump to [SageMaker Canvas](sagemaker.md) or use a forecasting library directly via SageMaker training jobs.**

## TL;DR

- Forecast was AWS's specialized service for time-series forecasting — demand planning, financial forecasts, capacity planning, energy load forecasting.
- Pre-built **predictors** based on Amazon-developed algorithms (DeepAR+, CNN-QR, Prophet, NPTS, ARIMA, ETS) plus the option to train ensembles automatically (AutoPredictor).
- Brought-your-own time-series data; Forecast generated probabilistic forecasts with confidence intervals.
- AWS shifted investment to **SageMaker Canvas** (no-code) and SageMaker AI (custom forecasting via your own pipelines), which give equivalent capabilities with broader integration and lower cost in 2026.

## When to use it

- **Existing customers only.** Migrate when feasible.
- **For new work: use [SageMaker Canvas](sagemaker.md)** (no-code, integrated with Studio), or train forecasting models directly via SageMaker Training Jobs (DeepAR, Prophet via custom containers, your own models).

## When NOT to use it

- New onboarding — blocked by AWS.
- Tasks where a simpler model (ETS / ARIMA in Python / R) is sufficient — sometimes the managed service is overkill.

## Key concepts (for existing users)

### Datasets

- **Target time series (TTS)** — the values you want to forecast.
- **Related time series (RTS)** — covariates (price, promotion flag, weather).
- **Item metadata (IM)** — static features per item (category, brand).

### Predictors

- **AutoPredictor** — Forecast trains an ensemble and picks the best per-item algorithm; the recommended default.
- **Manual algorithm choice** — pick from DeepAR+, CNN-QR, Prophet, NPTS, ARIMA, ETS.

### Forecasts

- Output stored in S3 or queryable via the QueryForecast API.
- Probabilistic — multiple quantiles (P10 / P50 / P90) rather than a single value.

### What-If analyses

Compare forecasts under different RTS scenarios (e.g., "if we cut price by 10%, what's the demand?").

## Migration to SageMaker Canvas

Canvas's time-series forecasting:

- No-code UI, similar dataset model (TTS / RTS / metadata).
- Ensembles multiple algorithms; picks the best per item.
- Output to S3, exportable to QuickSight.
- Pay only for SageMaker compute used during training and inference (cheaper at most scales than Forecast's per-prediction pricing).

Migration steps (AWS-published guidance):

1. Export your Forecast datasets and predictors to S3.
2. Re-create the datasets in Canvas.
3. Train a Canvas time-series model.
4. Validate predictions against your Forecast baseline.
5. Cut over downstream consumers.

For more advanced workloads — custom algorithms, complex pipelines, integration with other ML pipelines — train forecasting models directly via SageMaker Training Jobs.

## Pricing model (legacy)

- Per data-import volume + per algorithm-hour + per quantile-per-forecast.
- Predictor and Forecast resources billed for storage.

Largely irrelevant for new work; documented here only for context.

## Common pitfalls (for existing users / migration)

- **No migration plan.** Eventually Forecast will sunset further. Plan the move while you have time.
- **Lift-and-shift to Canvas without re-evaluating algorithms.** Canvas's algorithm picks may differ from Forecast's; validate accuracy before cutover.
- **Forgetting downstream consumers.** Anything that calls Forecast's QueryForecast API needs to be updated to read from S3 / a Canvas output.
- **Forecast as "the only forecasting in the org" without a contingency.** Build the new pipeline in parallel; don't switch in a single cutover.

## Pairs well with these repo pages

- [SageMaker](sagemaker.md) — Canvas and Training Jobs are the recommended path forward.
- [Timestream for InfluxDB](../database/timestream.md) — for the time-series storage piece of forecasting pipelines.
- [QuickSight](../analytics/quicksight.md) — visualization of forecasts.
- [S3](../storage/s3.md) — dataset and output storage.

## Further reading

- [Amazon Forecast documentation](https://docs.aws.amazon.com/forecast/).
- [Transition Forecast usage to SageMaker Canvas](https://aws.amazon.com/blogs/machine-learning/transition-your-amazon-forecast-usage-to-amazon-sagemaker-canvas/).
- [SageMaker Canvas time-series forecasting](https://docs.aws.amazon.com/sagemaker/latest/dg/canvas-time-series.html).
- [AWS Lifecycle Changes](https://aws.amazon.com/products/lifecycle/).
