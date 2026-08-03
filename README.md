# MiniMax H3 Hybrid Cond

ComfyUI custom node for MiniMax H3 conditioning. It supports both reference-to-video (`ref2va` / R2V) and first/last-frame video conditioning (`fl2va` / I2V), including a hybrid mode that uses both in one conditioning payload.

## Install

Copy `minimax_h3_hybrid` into:

```text
ComfyUI/custom_nodes/
```

Restart ComfyUI and search for:

```text
MiniMax H3 Hybrid Cond (R2V + I2V)
```

Required model inputs are the H3 video VAE, H3 audio VAE, and the matching H3 CLIP/text encoder. The node outputs a positive conditioning and an AV latent with native audio.

## Input mapping

| Node input | H3 function | Prompt tag |
|---|---|---|
| `first_frame` | `fl2va` keyframe at frame 0 | Not a Picture tag by default |
| `last_frame` | `fl2va` final keyframe | Not a Picture tag |
| `ref_image_1` | `ref2va` image reference | `<Picture 1>` |
| `ref_image_2` | `ref2va` image reference | `<Picture 2>` |
| `ref_video_1` | `ref2va` video reference | `<Video 1>` |
| `ref_audio_1` | `ref2va` audio reference | `<Audio 1>` |

Reference numbering follows the order of the connected reference inputs. Set `also_ref_first_frame` to `true` only when the first frame should also become the next Picture reference; it is appended after user reference images.

## 1. R2V-only example

Use this when the video should be controlled by reference media without an I2V start frame.

```text
first_frame: empty
last_frame: empty
ref_image_1: cat reference image
ref_image_2: optional character or style reference
also_ref_first_frame: false
```

Prompt:

```text
<Picture 1> is the main cat character. Preserve its identity, face, colors,
clothing, proportions, and silhouette. The cat walks forward and jumps toward
the camera in a cute exaggerated cartoon animation. Use <Picture 2> only for
secondary appearance guidance. Keep the background clean and the motion readable.
```

This uses `minimax_refs` with image reference blocks and `<Picture N>` tags. No keyframe is supplied.

## 2. fl2va / I2V-only example

Use this when the first image must be locked as the opening frame.

```text
first_frame: woman opening image
last_frame: optional final image
ref_image_1: empty
also_ref_first_frame: false
```

Prompt:

```text
Start exactly from the first frame. Preserve the woman's identity, composition,
lighting, background, rendering, and visual style. She slowly looks forward,
then reacts with a cute exaggerated surprise. Keep frame 0 stable and animate
only the requested motion.
```

This uses `minimax_keyframes` for `fl2va`. The first frame is a keyframe, not `<Picture 1>`.

## Hybrid: first frame + reference image with either H3 model

The same Hybrid node combines both inputs in one conditioning payload:

```text
first_frame  → woman image / opening keyframe
ref_image_1  → cat image / identity reference
```

Use the workflow with either H3 diffusion checkpoint.

### Variant A: fl2va model

```text
Load Diffusion Model: minimax_h3_fl2va_bf16.safetensors
first_frame: connected
ref_image_1: connected
last_frame: optional
also_ref_first_frame: false
```

This is preferred when locking the first frame is the main priority. The first frame becomes the opening keyframe and the cat becomes `<Picture 1>`.

### Variant B: ref2va model

```text
Load Diffusion Model: minimax_h3_ref2va_bf16.safetensors
first_frame: connected
ref_image_1: connected
last_frame: optional
also_ref_first_frame: false
```

This is preferred when the cat identity/reference is the main priority. The same first-frame keyframe and `<Picture 1>` reference are supplied together.

### Shared prompt

```text
The first frame is the authoritative source for the woman's identity,
opening composition, camera, white background, lighting, rendering, and style.
<Picture 1> is the authoritative source for the cat's identity, face, colors,
clothing, proportions, and silhouette. The cat suddenly jumps forward and
clings to the woman's face in a cute, harmless, exaggerated cartoon action.
Preserve both characters and keep the motion readable.
```

The node combines both payload sections internally:
## Native audio

Connect `ref_audio_1` for an audio reference, or use the H3 audio VAE output for generated native audio. Keep dialogue, sound effects, and timing instructions in the prompt. The node always creates the H3 audio/video latent pair.

## Important settings

- `length` is measured in frames and uses a 24 fps workflow. For approximately 5 seconds use `124` frames.
- `ref_image_size=match` is required for identity/style fidelity. You need to set the ref image size to `Match`. If you set it to `Max`, the identity/style may get distorted.
- `width` and `height` should be multiples of 32.
- `ref_image_size=match` preserves the relative reference image size; `max` limits the reference short edge.
- Do not combine separate H3 I2V and R2V conditioning nodes for the same sample. Use this Hybrid node so the packed layout and latent order remain consistent.
