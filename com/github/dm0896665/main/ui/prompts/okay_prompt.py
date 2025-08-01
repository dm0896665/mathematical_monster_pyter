from com.github.dm0896665.main.ui.prompt import Prompt
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption


class OkayPrompt(Prompt):
    def __init__(self, prompt_text: str):
        super().__init__(prompt_text, PromptOption.OKAY)