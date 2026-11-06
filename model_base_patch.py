"""Runtime patch for MiniMax H3 hybrid conditioning.

Kept in this custom node so the Comfy core remains untouched. The upstream H3
extra_conds builds the layout metadata correctly but its visual latent list is
last-writer-wins when keyframes and refs coexist; this wrapper preserves the
same order as PackedLayout.
"""

_PATCHED = False


def install_hybrid_payload_patch():
    global _PATCHED
    if _PATCHED:
        return
    from comfy.model_base import MiniMaxH3

    original = MiniMaxH3.extra_conds

    def extra_conds_with_hybrid(self, **kwargs):
        output = original(self, **kwargs)
        holder = output.get("minimax_payload")
        if holder is None or not isinstance(getattr(holder, "cond", None), dict):
            return output

        keyframes = kwargs.get("minimax_keyframes")
        refs = kwargs.get("minimax_refs")
        visual_latents = []
        if keyframes is not None:
            visual_latents.extend(item["latent"] for item in keyframes if item.get("latent") is not None)
        if refs is not None:
            visual_latents.extend(item["latent"] for item in refs if item.get("latent") is not None)
        if visual_latents:
            holder.cond["cond_video_latents"] = visual_latents

        audio_latents = [
            item["audio_latent"] for item in (keyframes or [])
            if item.get("audio_latent") is not None
        ]
        if refs is not None:
            audio_latents.extend(
                item["audio_latent"]
                for item in refs
                if item.get("audio_latent") is not None
            )
        if audio_latents:
            holder.cond["cond_audio_latents"] = audio_latents
        return output

    MiniMaxH3.extra_conds = extra_conds_with_hybrid
    MiniMaxH3._minimax_hybrid_payload_patch = True
    _PATCHED = True
