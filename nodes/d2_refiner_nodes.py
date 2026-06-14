import math

from comfy_api.latest import io


"""

D2_RefinerSteps
Refinerの切り替えステップをステップ数で指定する

"""
class D2_RefinerSteps(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Refiner Steps",
            display_name="D2 Refiner Steps",
            category="D2/Refiner",
            inputs=[
                io.Int.Input("steps", default=25, min=0),
                io.Int.Input("start", default=0, min=0),
                io.Int.Input("end", default=5, min=0),
            ],
            outputs=[
                io.Int.Output(display_name="steps"),
                io.Int.Output(display_name="start"),
                io.Int.Output(display_name="end"),
                io.Int.Output(display_name="refiner_start"),
            ],
        )

    @classmethod
    def execute(cls, steps, start, end) -> io.NodeOutput:
        refiner_start = end + 1
        return io.NodeOutput(steps, start, end, refiner_start)



"""

D2 Refiner Steps A1111
Refinerの切り替えステップを％で指定する

"""
class D2_RefinerStepsA1111(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Refiner Steps A1111",
            display_name="D2 Refiner Steps A1111",
            category="D2/Refiner",
            inputs=[
                io.Int.Input("steps", default=25),
                io.Float.Input("denoise", default=1, min=0, max=1, step=0.01),
                io.Float.Input("switch_at", default=0.2, min=0, max=1, step=0.01),
            ],
            outputs=[
                io.Int.Output(display_name="steps"),
                io.Int.Output(display_name="start"),
                io.Int.Output(display_name="end"),
                io.Int.Output(display_name="refiner_start"),
            ],
        )

    @classmethod
    def execute(cls, steps, denoise, switch_at) -> io.NodeOutput:
        real_steps = math.floor(steps / denoise)
        start = real_steps - steps
        end = math.floor((real_steps - start) * switch_at) + start
        refiner_start = end + 1

        return io.NodeOutput(real_steps, start, end, refiner_start)




"""

D2 Refiner Steps Tester
Refiner Steps の計算結果を確認するノード

"""
class D2_RefinerStepsTester(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="D2 Refiner Steps Tester",
            display_name="D2 Refiner Steps Tester",
            category="D2/Refiner",
            is_output_node=True,
            inputs=[
                io.Int.Input("steps", force_input=True, optional=True),
                io.Int.Input("start", force_input=True, optional=True),
                io.Int.Input("end", force_input=True, optional=True),
                io.Int.Input("refiner_start", force_input=True, optional=True),
                io.String.Input("text", multiline=True, optional=True),
            ],
            outputs=[],
        )

    @classmethod
    def execute(cls, steps=0, start=0, end=0, refiner_start=0, text="") -> io.NodeOutput:
        output = f"stesps: {steps}\nstart: {start}\nend: {end}\nrefiner_start: {refiner_start}"
        return io.NodeOutput(ui={"text": (output,)})




NODE_CLASS_MAPPINGS = {
    "D2 Refiner Steps": D2_RefinerSteps,
    "D2 Refiner Steps A1111": D2_RefinerStepsA1111,
    "D2 Refiner Steps Tester": D2_RefinerStepsTester,
}


