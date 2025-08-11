from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption
from com.github.dm0896665.main.ui.prompts.multichoice_prompt import MultichoicePrompt


class OnOffPrompt(MultichoicePrompt):
    def __init__(self, prompt_text: str):
        super().__init__(prompt_text, PromptOption.ON, PromptOption.OFF)