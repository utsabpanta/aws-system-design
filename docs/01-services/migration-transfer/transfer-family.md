# Transfer Family

> **One-line summary.** Fully managed SFTP, FTPS, FTP, AS2, and web file transfer service. Replaces self-managed SFTP / B2B EDI servers; lands files directly in S3 or EFS.

## TL;DR
- The right service when "we need to receive files from partners / vendors / suppliers" or "we need to expose an SFTP endpoint to a customer."
- Five protocols supported: **SFTP** (most common), **FTPS**, **FTP** (legacy), **AS2** (B2B EDI for retail / healthcare / logistics), and **web browser-based transfers**.
- Files land in **S3** or **EFS**; pricing is per-protocol-endpoint-hour + per-GB transferred.
- **Managed File Transfer Workflows** automates post-upload processing (decrypt, decompress, virus-scan, route, transform, archive) — serverless, no Lambda glue needed.
- **SFTP Connectors** are the inverse direction — outbound SFTP to a partner's server, no always-on infra.

## When to use it
- Replacing a self-hosted SFTP server (cron + sshd + cleanup scripts) with managed.
- Partner / vendor / customer file exchange (orders, invoices, logs, batch data).
- B2B EDI exchange via AS2 (the protocol most of retail / healthcare / pharma uses).
- Web-browser-based file upload portals (without building your own).
- One-off outbound SFTP transfers to partner systems (SFTP Connectors).

## When NOT to use it
- Sync / migration between AWS and on-prem — use **DataSync**.
- Database migration — use **DMS**.
- Live file-share access by applications — use **EFS** / **FSx** with native mounts.
- Tiny / very-low-volume SFTP — managed pricing (per-protocol-hour ≈ $216/month always-on baseline) doesn't amortize for occasional use.

## Key concepts

### Protocols
- **SFTP** — most common; SSH-tunneled file transfer.
- **FTPS** — FTP over TLS.
- **FTP** — plaintext FTP (legacy; not recommended for sensitive data).
- **AS2** — B2B EDI standard with signed / encrypted / MDN-receipted messages.
- **Web browser transfers** — upload via web UI.

### Servers and endpoints
- **Server** — the Transfer Family resource that exposes one or more protocol endpoints.
- **Endpoint type**:
  - **Public** — internet-facing.
  - **VPC-internal** — only reachable from your VPC.
  - **VPC with internet access** — VPC endpoint with public IPs.

### Storage destinations
- **Amazon S3** — most common destination.
- **Amazon EFS** — for legacy apps that expect POSIX file access.

### Identity providers
- **Service-managed** — Transfer Family stores user records and SSH keys.
- **AWS Directory Service** — Active Directory authentication.
- **Custom (Lambda)** — your own auth logic (e.g., authenticate against an external IdP, look up credentials in Secrets Manager).

### Managed File Transfer Workflows
- Trigger on file upload.
- Steps: copy, tag, decrypt, decompress, scan (via Lambda or container), filter, transform, archive.
- Serverless — no Lambda + EventBridge plumbing to build.

### SFTP Connectors
- **Outbound** SFTP connections.
- Connect on demand to a partner's SFTP server, send / receive files, disconnect.
- Pay per call + per GB — no always-on cost (unlike Transfer Family servers).
- The right pattern for "we need to push files to a partner's SFTP" without standing up our own server.

### AS2
- **Connectors** for AS2 outbound to partners; **servers** for AS2 inbound.
- Manage **profiles** (your AS2 ID + cert), **certificates** (signing / encryption), **partnerships** (your-to-their pairing).
- Supports MDN (receipt) acknowledgments.

### Custom hostnames
- Bring your own DNS name (and TLS cert via ACM) for the server endpoint.

### Logging & monitoring
- CloudWatch Logs for transfer activity.
- CloudWatch Metrics for connection / file-count / byte counts.

## Pricing model

- **Protocol endpoint hours**: ~$0.30 / hour per protocol per server (~$216 / month per always-on SFTP endpoint).
- **Data transfer**: $0.04 / GB transferred (SFTP / FTPS / FTP).
- **AS2 messages**: per-message pricing; contact AWS for high volumes (>1M messages/month).
- **SFTP Connectors**: $0.001 / call + $0.40 / GB sent or retrieved. Much cheaper for bursty / occasional use.
- **Web app**: separate pricing for the browser-upload feature.

For always-on SFTP servers, baseline is several hundred dollars / month. For occasional outbound transfers, SFTP Connectors are dramatically cheaper.

## Quotas & limits

- **Servers per account per Region**: 100 default.
- **Concurrent connections per server**: high (1,000s).
- **Users per server**: 10,000 default.
- **File size per upload**: bounded by S3 / EFS (effectively very large).
- **SFTP Connectors**: bounded per account; check current docs.

## Common pitfalls

- **One protocol per server.** You pay per protocol per server hour. Consolidate where possible.
- **Public endpoint when VPC-internal would do.** Public exposure is a risk surface; use VPC-internal for partner connections via VPN / Direct Connect.
- **Service-managed identity at scale.** Becomes a chore. AD or custom Lambda IdP scales better.
- **No Workflows for post-upload processing.** Per-upload Lambdas chained ad hoc grow brittle. Use Workflows.
- **AS2 partnerships configured without certificate rotation plan.** AS2 certs expire; without monitoring, partnerships break silently.
- **Always-on SFTP server for occasional outbound transfers.** Use SFTP Connectors instead — pay only per call.
- **No CloudWatch alarms on transfer failures.** Failed uploads / processing errors stay invisible.
- **Default unencrypted FTP.** Don't.

## Pairs well with
- [S3](../storage/s3.md), [EFS](../storage/efs.md) — file destinations.
- [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md) — custom processing.
- [Secrets Manager](../security-identity/secrets-manager.md) — credentials for custom IdPs.
- **AWS Directory Service** — AD-based user auth.
- [Route 53](../networking/route53.md), [ACM](../security-identity/acm.md) — custom hostnames and TLS.
- [DataSync](datasync.md) — sibling for sync / migration; different use case.

## Pairs well with these repo pages
- [S3](../storage/s3.md), [Lambda](../compute/lambda.md), [Step Functions](../integration-messaging/step-functions.md), [DataSync](datasync.md).

## Further reading
- [AWS Transfer Family documentation](https://docs.aws.amazon.com/transfer/).
- [Managed File Transfer Workflows](https://docs.aws.amazon.com/transfer/latest/userguide/transfer-workflows.html).
- [SFTP Connectors](https://docs.aws.amazon.com/transfer/latest/userguide/creating-server.html#sftp-connectors-overview).
- [AS2 in Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/create-server-as2.html).
- [Custom identity providers](https://docs.aws.amazon.com/transfer/latest/userguide/custom-identity-provider-users.html).
