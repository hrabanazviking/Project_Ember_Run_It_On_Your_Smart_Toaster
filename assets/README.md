# assets/

Binary and large media files referenced from the documentation: images, audio samples, video clips, diagrams, screenshots.

## Rules

- All references to assets from `.md` files use **relative paths** (`./assets/<name>`), never absolute GitHub raw URLs. This is the Law of Flexible Roots — a clone in any location must render correctly.
- Original-resolution sources stay here. Don't downscale to "save space" — Git handles binary blobs adequately and the lossy version belongs in the destination doc, not here.
- File names should be meaningful when possible. UUID-named images carried over from earlier stages are tolerated until they are referenced by something meaningful enough to justify renaming.
- One-time license images (e.g. the MIT license illustration) are filed here too rather than in a separate folder; license *text* lives in `LICENSE` at repo root.
