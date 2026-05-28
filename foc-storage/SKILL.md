---
name: foc-storage
description: Store, price, and manage files on Filecoin Onchain Cloud through @fil-b/foc-storage-mcp. Use for upload, dataset, provider, balance, payment, withdrawal, and storage-cost requests.
metadata: {"clawdbot":{"emoji":"🗄️","requires":{"bins":["node","npx","mcporter"]},"primaryEnv":"FOC_STORAGE_PRIVATE_KEY","install":[{"id":"mcporter-node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (node)"}]}}
---

# FOC Storage

Use the FOC Storage MCP server to operate Filecoin Onchain Cloud storage.

## Runtime

The repo includes an `mcporter` config at `./config/mcporter.json` and a stdio
wrapper at `{baseDir}/scripts/foc-storage-mcp.sh`.

Preferred command shape from the workspace root:

```bash
mcporter call --config ./config/mcporter.json foc-storage.<toolName> --args '<json>' --output markdown
```

Ad-hoc command shape when the config is unavailable:

```bash
mcporter call --stdio "{baseDir}/scripts/foc-storage-mcp.sh" <toolName> --args '<json>' --output markdown
```

Before first use, confirm `FOC_STORAGE_PRIVATE_KEY` is available through the
environment or `skills.entries.foc-storage.apiKey`. Do not echo secret values.
Default to `FILECOIN_NETWORK=calibration` unless the user explicitly requests
mainnet.

## Safe Operating Rules

- Never expose private keys, wallet seeds, or `.env` contents.
- Ask for explicit confirmation before state-changing tools:
  `uploadFile`, `createDataset`, `processPayment`, and `processWithdrawal`.
- For uploads, use `autoPayment:false` unless the user explicitly authorizes
  automatic payment.
- Before payment or withdrawal, state the amount in USDFC and network.
- Before upload, state file path, CDN choice, dataset choice, and whether
  payment is allowed.
- Warn when balance is under 45 days. Under 30 days, explain that storage
  providers may consider the account insolvent.
- Prefer existing datasets with matching CDN/provider settings instead of
  creating new datasets unnecessarily.

## Workflows

Balance check:

1. Ask whether the user wants defaults or custom capacity/duration.
2. Call `getBalances`.
3. Report FIL, USDFC, available storage funds, days remaining, deposit needed,
   and allowance sufficiency.

Pricing:

1. Convert user-provided size to GiB/TiB when needed.
2. Call `estimateStoragePricing` for concrete estimates or
   `getStoragePricingInfo` for model explanation.
3. Include the 30-day insolvency threshold and recommended 45-day buffer.

Upload:

1. Confirm the file path is absolute and readable.
2. Check balance first.
3. Confirm CDN, dataset ID, metadata, network, and payment behavior.
4. Call `uploadFile`.
5. Return piece CID, retrieval URL, transaction hash, file name, file size, and
   progress log highlights.

Datasets/providers:

1. Use `getProviders` before creating a dataset because `providerId` is
   required.
2. Use `getDatasets` or `getDataset` to inspect existing storage.
3. Create datasets only after confirming provider, CDN setting, and metadata.

## Tool Reference

For exact tool names, arguments, and examples, read:

- `{baseDir}/references/foc-storage-tools.md`
