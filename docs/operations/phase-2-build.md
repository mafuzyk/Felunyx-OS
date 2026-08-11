# Phase 2 build operations

## Validate without privilege

```bash
make validate
```

## Build the canonical environment

```bash
docker build -t felunyx-phase2-builder -f build/Containerfile .
```

## Frozen build

```bash
mkdir -p artifacts
docker run --rm --privileged \
  -v "$PWD:/workspace" -w /workspace \
  felunyx-phase2-builder \
  'tools/felunyx-build --mode frozen --archive-date 2026/07/27 --output /workspace/artifacts'
```

## Integration build

Replace the final command with:

```bash
tools/felunyx-build --mode integration --output /workspace/artifacts
```

Frozen builds never fall through to current mirrors. Before removing a failed work tree, inspect it with `findmnt`; the build refuses deletion while a submount remains.
