from typing import Optional
from comfy_extras.nodes_model_merging import ModelMergeBlocks, CLIPMergeSimple

class D2_ModelAndCLIPMergeSDXL():
    CATEGORY = "advanced/model_merging/model_specific"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "model1": ("MODEL",),
                "model2": ("MODEL",),
                "clip1": ("CLIP",),
                "clip2": ("CLIP",),
                "weights": ("STRING",),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP",)
    FUNCTION = "merge"
    CATEGORY = "D2/Merge"

    def merge(self, model1, model2, clip1, clip2, weights):
        # Parse weights string into dictionary
        weight_parts = [w.strip() for w in weights.split(",")]
        weights_dict = {}
        
        # SDXL model structure components
        components = [
            "time_embed.",
            "label_emb.",
            "input_blocks.0", "input_blocks.1", "input_blocks.2", "input_blocks.3",
            "input_blocks.4", "input_blocks.5", "input_blocks.6", "input_blocks.7", "input_blocks.8",
            "middle_block.0", "middle_block.1", "middle_block.2",
            "output_blocks.0", "output_blocks.1", "output_blocks.2", "output_blocks.3",
            "output_blocks.4", "output_blocks.5", "output_blocks.6", "output_blocks.7", "output_blocks.8",
            "out"
        ]

        # Map weights to components
        for i, weight in enumerate(weight_parts):
            if i < len(components):
                try:
                    weight_float = float(weight)
                    weights_dict[components[i]] = weight_float
                except ValueError:
                    weights_dict[components[i]] = 0.5  # Default to 0.5 if invalid weight

        # Fill remaining components with default weight
        for comp in components:
            if comp not in weights_dict:
                weights_dict[comp] = 0.5

        # Calculate CLIP merge ratio (last weight if provided, otherwise 0.5)
        clip_ratio = float(weight_parts[-1]) if len(weight_parts) > len(components) else 0.5

        # Merge models using ModelMergeBlocks
        model_merger = ModelMergeBlocks()
        merged_model = model_merger.merge(model1, model2, **weights_dict)[0]

        # Merge CLIP models
        clip_merger = CLIPMergeSimple()
        merged_clip = clip_merger.merge(clip1, clip2, clip_ratio)[0]

        return (merged_model, merged_clip,)


NODE_CLASS_MAPPINGS = {
    "D2 Model and CLIP Merge SDXL": D2_ModelAndCLIPMergeSDXL,
}
