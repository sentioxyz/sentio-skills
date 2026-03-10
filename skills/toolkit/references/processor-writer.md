# Processor Writer Playbook

## Goal
Generate production-ready Sentio processor code using proven patterns from `sentio-sdk/examples`.

## Inputs to collect
- Chain and SDK module: `eth`, `aptos`, `sui`, `solana`, `fuel`, or others.
- Contract/object targets: address/object ID/network/start block or start version.
- Trigger types: event, call/entry, block interval, time interval, transaction, object change.
- Outputs: metrics, event logs, exporter payloads, stored entities.
- Constraints: filters, include failed txns, end block, expected labels.

## Bootstrap with Sentio CLI (required)
Start every processor-writing task from a generated project scaffold:
- `npx @sentio/cli@latest create <project-name> -c <chain-type>`
- For EVM default-mainnet scaffolds: add `--chain-id 1`.
- For monorepo workspaces: add `--subproject`.
- Prefer `yarn` or `pnpm` over `npm` for install/init workflows when the environment supports them.
- Prefer editing generated `src/processor.ts` output over creating files from scratch.

## Writer workflow
1. Initialize project with Sentio CLI and confirm starter `src/processor.ts` exists.
2. Select processor type and imports.
3. Declare meters/loggers/exporters once at file top.
4. Bind processor with explicit config (`address`, `network`, `startBlock` or `startVersion`).
5. Add handlers with explicit trigger names and optional filters.
6. Normalize numeric values before writing metrics or entities.
7. Persist state with `ctx.store` when values must survive restarts.
8. Add or update minimal `src/processor.test.ts` using `TestProcessorServer`.

## EVM template (event filter + block interval)
```ts
import { Counter, Gauge } from '@sentio/sdk'
import { ERC20Processor } from '@sentio/sdk/eth/builtin'

const transferVolume = Counter.register('transfer_volume')
const tokenBalance = Gauge.register('token_balance')

const transferFilter = ERC20Processor.filters.Transfer(
  '0x0000000000000000000000000000000000000000',
  '0xYourTargetAddress'
)

ERC20Processor.bind({ address: '0xTokenAddress', startBlock: 12345678 })
  .onEventTransfer(async (event, ctx) => {
    const amount = event.args.value.scaleDown(18)
    transferVolume.add(ctx, amount, { token: 'TOKEN' })
  }, transferFilter)
  .onBlockInterval(async (_, ctx) => {
    const balance = await ctx.contract.balanceOf('0xYourTargetAddress')
    tokenBalance.record(ctx, balance.scaleDown(18), { token: 'TOKEN' })
  })
```

## Aptos template (entry + event + network)
```ts
import { coin } from '@sentio/sdk/aptos/builtin/0x1'
import { AptosNetwork } from '@sentio/sdk/aptos'

coin.bind({ network: AptosNetwork.MAIN_NET })
  .onEventWithdrawEvent((evt, ctx) => {
    ctx.meter.Counter('withdraw_count').add(1)
    ctx.meter.Counter('withdraw_amount').add(evt.data_decoded.amount)
  })
```

## Sui template (object/time interval)
```ts
import { SuiObjectTypeProcessor } from '@sentio/sdk/sui'
import { staking_pool } from '@sentio/sdk/sui/builtin/0x3'

SuiObjectTypeProcessor.bind({
  objectType: staking_pool.StakedSui.type()
}).onTimeInterval((self, _, ctx) => {
  ctx.meter.Gauge('voting_power').record(self.data_decoded.principal)
}, 60)
```

## Fuel template (transaction + failed tx support)
```ts
import { LogLevel } from '@sentio/sdk'
import { FuelNetwork } from '@sentio/sdk/fuel'
import { CounterContractProcessor } from './types/fuel/CounterContractProcessor.js'

CounterContractProcessor.bind({
  chainId: FuelNetwork.TEST_NET,
  address: '0xContractAddress'
}).onTransaction((tx, ctx) => {
  ctx.eventLogger.emit('transaction', {
    distinctId: tx.id,
    message: 'Transaction processed',
    severity: tx.status === 'success' ? LogLevel.INFO : LogLevel.ERROR
  })
}, { includeFailed: true })
```

## Entity Store pattern
- Define entities in `schema.graphql`.
- Generate schema artifacts with `sentio build`.
- Use `ctx.store.upsert/get/list/listIterator/delete` inside handlers.
- Prefer `listIterator` for large scans.

## Minimum test file
```ts
import assert from 'assert'
import { before, describe, test } from 'node:test'
import { TestProcessorServer } from '@sentio/sdk/testing'

describe('Processor smoke test', () => {
  const service = new TestProcessorServer(async () => await import('./processor.js'))

  before(async () => {
    await service.start()
  })

  test('has contract config', async () => {
    const config = await service.getConfig({})
    assert(config.contractConfigs.length > 0)
  })
})
```

## Quality gates before handoff
- Metric names and labels follow Sentio naming rules in `references/metrics.md`.
- No global mutable state used for persistent business data.
- Handler triggers match the requested chain and contract/object semantics.
- Commands provided: `sentio test` then `sentio build`.
- Include `sentio upload` only when deployment is requested.

## Example source pointers
- `examples/x2y2/src/processor.ts` for EVM event filters and block intervals.
- `examples/x2y2-database/src/processor.ts` for Entity Store writes and reads.
- `examples/aptos/src/processor.ts` for Aptos event and entry handlers.
- `examples/sui/src/processor.ts` for Sui object and time interval handlers.
- `examples/fuel-counter/src/processor.ts` for `includeFailed` transactions and event logging.

## Merge strategy with official examples
- Keep generated imports and config style from `sentio create`.
- Copy only handler logic patterns from `sentio-sdk/examples` and adapt addresses, network, and labels.
- Re-run `sentio test` after each major handler addition.
