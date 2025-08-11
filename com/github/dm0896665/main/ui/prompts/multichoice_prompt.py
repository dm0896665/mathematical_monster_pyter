from com.github.dm0896665.main.ui.prompt import Prompt
from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOptionButton, PromptOption


class MultichoicePrompt(Prompt[PromptOption]):
    def __init__(self, prompt_text: str, *button_options: PromptOption):
        super().__init__(prompt_text, *button_options)