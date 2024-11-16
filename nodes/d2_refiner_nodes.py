import math


"""

D2_RefinerSteps
Refinerの切り替えステップをステップ数で指定する

"""
class D2_RefinerSteps:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 25, "min":0}),
                "start": ("INT", {"default": 0, "min":0}),
                "end": ("INT", {"default": 5, "min":0}),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT", "INT",)
    RETURN_NAMES = ("steps", "start", "end", "refiner_start",)
    FUNCTION = "run"
    CATEGORY = "D2/Refiner"

    def run(self, steps, start, end):
        refiner_start = end + 1
        return(steps, start, end, refiner_start,)



"""

D2 Refiner Steps A1111
Refinerの切り替えステップを％で指定する

"""
class D2_RefinerStepsA1111:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "steps": ("INT", {"default": 25}),
                "denoise": ("FLOAT", {"default": 1, "min":0, "max":1, "step":0.01}),
                "switch_at": ("FLOAT", {"default": 0.2, "min":0, "max":1, "step":0.01}),
            }
        }
    RETURN_TYPES = ("INT", "INT", "INT", "INT",)
    RETURN_NAMES = ("steps", "start", "end", "refiner_start",)
    FUNCTION = "run"
    CATEGORY = "D2/Refiner"

    def run(self, steps, denoise, switch_at):
        real_steps = math.floor(steps / denoise)
        start = real_steps - steps
        end = math.floor((real_steps - start) * switch_at) + start
        refiner_start = end + 1

        return(real_steps, start, end, refiner_start,)




"""

D2 Refiner Steps Tester
Refiner Steps の計算結果を確認するノード

"""
class D2_RefinerStepsTester:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "steps": ("INT", {"forceInput":True}),
                "start": ("INT", {"forceInput":True}),
                "end": ("INT", {"forceInput":True}),
                "refiner_start": ("INT", {"forceInput":True}),
                "text": ("STRING", {"multiline":True}),
            }
        }

    # INPUT_IS_LIST = True
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "run"
    CATEGORY = "D2/Refiner"

    def run(self, steps=0, start=0, end=0, refiner_start=0, text=""):
        output = f"stesps: {steps}\nstart: {start}\nend: {end}\nrefiner_start: {refiner_start}"
        return {
            "ui": {"text": (output,)},
            "result": (output,)
        }




NODE_CLASS_MAPPINGS = {
    "D2 Refiner Steps": D2_RefinerSteps,
    "D2 Refiner Steps A1111": D2_RefinerStepsA1111,
    "D2 Refiner Steps Tester": D2_RefinerStepsTester,
}


