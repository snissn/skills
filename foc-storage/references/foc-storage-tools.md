# FOC Storage MCP Tool Reference

The MCP server is `@fil-b/foc-storage-mcp`. It currently exposes these tools:

- `uploadFile`
- `getDatasets`
- `getDataset`
- `createDataset`
- `getBalances`
- `processPayment`
- `processWithdrawal`
- `getProviders`
- `estimateStoragePricing`
- `getStoragePricingInfo`
- `convertStorageSize`

## Examples

List providers:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.getProviders \
  --args '{"onlyApproved":true}' \
  --output markdown
```

Estimate storage:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.estimateStoragePricing \
  --args '{"sizeInGiB":500,"durationInMonths":6,"createCDNDataset":false}' \
  --output markdown
```

Get pricing info:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.getStoragePricingInfo \
  --args '{"includeCDNExample":true}' \
  --output markdown
```

Check balances for defaults:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.getBalances \
  --args '{}' \
  --output markdown
```

Check balances for 500 GiB over one year:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.getBalances \
  --args '{"storageCapacityBytes":536870912000,"persistencePeriodDays":365,"notificationThresholdDays":45}' \
  --output markdown
```

Upload without automatic payment:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.uploadFile \
  --args '{"filePath":"/absolute/path/report.pdf","withCDN":false,"autoPayment":false,"metadata":{"purpose":"report"}}' \
  --output markdown
```

Create a dataset:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.createDataset \
  --args '{"withCDN":false,"providerId":"123","metadata":{"project":"demo"}}' \
  --output markdown
```

Deposit USDFC:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.processPayment \
  --args '{"depositAmount":1}' \
  --output markdown
```

Withdraw USDFC:

```bash
mcporter call --config ./config/mcporter.json \
  foc-storage.processWithdrawal \
  --args '{"withdrawalAmount":1}' \
  --output markdown
```

## Argument Notes

`uploadFile`:

- `filePath`: absolute path to local file.
- `fileName`: optional stored filename.
- `metadata`: optional string map, at most four key-value pairs.
- `datasetId`: optional existing dataset ID.
- `withCDN`: boolean; use for frequently accessed files.
- `autoPayment`: boolean; set `false` unless the user explicitly authorizes
  automatic payment.

`createDataset`:

- `providerId` is required. Call `getProviders` first.
- `withCDN:true` triggers a CDN payment/top-up.
- `metadata` supports up to ten string key-value pairs.

`getBalances`:

- Defaults are controlled by environment:
  `TOTAL_STORAGE_NEEDED_GiB=150`, `PERSISTENCE_PERIOD_DAYS=365`,
  `RUNOUT_NOTIFICATION_THRESHOLD_DAYS=45`.
- `storageCapacityBytes` is bytes, not GiB.

`processPayment` and `processWithdrawal`:

- Amounts are USDFC token units, not base units.
- Always confirm amount and network before calling.
