# Handlers and ctx Notes

## Handler types
- Event handlers react to contract events.
- Call handlers react to contract calls.
- Interval handlers run on a schedule for polling or aggregation.
- Filters can limit events by indexed fields to reduce workload.
- Transaction handlers can include failed transactions when configured.
- Object change handlers track state transitions for object-based chains.

## ctx capabilities
- `ctx.chain` provides chain-specific context and block/transaction metadata.
- `ctx.meter` creates and updates metrics.
- `ctx.eventLogger` emits event logs for later inspection.
- `ctx.exporter` exports custom data payloads.
- `ctx.store` reads and writes Entity Store data.
- `ctx.contract` provides typed on-chain reads for bound contract processors.
- `ctx.coder` supports event decoding and dynamic field access in chains like Aptos and Sui.
