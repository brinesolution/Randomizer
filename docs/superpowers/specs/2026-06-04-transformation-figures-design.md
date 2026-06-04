# Transformation Figures Design

## Goal

Replace the transformation section's text-only numbered blocks with truthful,
readable figures that explain how accepted source bytes become the final OTP.

## Figures

### Figure 3.1: Source bytes to source hashes

Each accepted source shows a compact sixteen-byte input strip, a directional
arrow, and a sixteen-byte preview of its SHA-512 digest. Exact full hashes stay
visible below the figure.

### Figure 3.2: Fusion convergence

An inline SVG routes each accepted source hash into one labeled HG-MSEF fusion
node. The figure is schematic: lines communicate stable convergence order, not
numeric magnitude.

### Figure 3.3: Conditioning comparison

The fused and conditioned SHA-512 digests appear as aligned 8 by 8 byte
heatmaps. Cell intensity encodes byte value from 0 to 255. Exact hexadecimal
digests remain visible for verification.

### Figure 3.4: Rejection sampling

An inline SVG number line shows the candidate inside the accepted range, the
acceptance boundary, and the small rejected tail up to the 32-bit maximum.
Labels show exact values because the rejected tail is too small to judge by
width alone.

## Data Contract

`build_transformation_visual` adds `rawPreview` to each source-hash item. The
existing source digest, fused digest, conditioned digest, candidate, limit,
inspected count, and uniform value remain unchanged.

## Presentation

Figures use the current Newsprint palette and sharp borders. Essential values
are directly labeled and remain available without hover. On mobile, source
figures and heatmaps stack vertically and SVG labels remain legible.

## Testing

- Unit test that each accepted source hash includes the exact first sixteen raw
  bytes.
- JavaScript and Python syntax checks.
- Full pytest suite.
- Desktop and mobile browser visual inspection.

