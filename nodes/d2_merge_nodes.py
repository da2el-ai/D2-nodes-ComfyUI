from typing import Optional
from comfy_extras.nodes_model_merging import ModelMergeBlocks, CLIPMergeSimple
from comfy_api.latest import io

class D2_ModelAndCLIPMergeSDXL(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Model and CLIP Merge SDXL",
            display_name="D2 Model and CLIP Merge SDXL",
            category="D2/Merge",
            inputs=[
                io.Model.Input("model1"),
                io.Model.Input("model2"),
                io.Clip.Input("clip1"),
                io.Clip.Input("clip2"),
                io.String.Input("weights"),
            ],
            outputs=[
                io.Model.Output(display_name="MODEL"),
                io.Clip.Output(display_name="CLIP"),
            ],
        )

    @classmethod
    def execute(cls, model1, model2, clip1, clip2, weights) -> io.NodeOutput:
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

        return io.NodeOutput(merged_model, merged_clip)


NODE_CLASS_MAPPINGS = {
    "D2 Model and CLIP Merge SDXL": D2_ModelAndCLIPMergeSDXL,
}
