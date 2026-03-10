# Entity Store Notes

## Schema and build
- Define entities in `store.graphql`.
- Enable decorators in `tsconfig.json` with `experimentalDecorators` and `emitDecoratorMetadata`.
- Run `sentio build` to generate typed entity classes from the schema.

## Store operations
- Use `ctx.store.upsert` to create or update entities.
- Use `ctx.store.get` or `ctx.store.getOrFail` to fetch by id.
- Use `ctx.store.delete` to remove entities.
- Use `ctx.store.list` for small collections and `ctx.store.listIterator` for large ones.

## Relationships
- Use `derivedFrom` for reverse relations.
- Entity Store data is isolated per chain.
