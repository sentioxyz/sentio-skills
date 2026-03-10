# Quickstart Notes

## Prerequisites
- Node.js environment.
- Sentio account for CLI login.

## CLI setup and login
- Use `npx @sentio/cli@latest login` to authenticate.

## Project creation
- Create a processor project with `npx @sentio/cli@latest create <project-name>`.
- Default is an EVM project. Use `-c <evm|aptos|solana|raw|fuel|sui|iota|starknet>` for other chains.
- For monorepos, use `--subproject` if your root package.json controls versions.

## Init from CLI examples
- EVM scaffold (includes ERC20 transfer processor example):
`npx @sentio/cli@latest create my-evm --directory . -c eth --chain-id 1`
- Aptos scaffold (includes entry + event handler examples):
`npx @sentio/cli@latest create my-aptos --directory . -c aptos`
- Sui scaffold (includes validator/object interval examples):
`npx @sentio/cli@latest create my-sui --directory . -c sui`
- After scaffold generation, edit `src/processor.ts` instead of writing from a blank file.

## Build and upload
- Run `sentio test` for local processor checks.
- Run `sentio build` to compile and generate bindings.
- Run `sentio upload` to deploy when explicitly requested.

## Common script pattern
- Use package scripts aligned with Sentio examples:
- `build`: `sentio build --skip-deps`
- `test`: `sentio test`
- `upload`: `sentio upload` (or `sentio upload --skip-deps` in monorepos)
