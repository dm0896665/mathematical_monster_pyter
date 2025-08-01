from com.github.dm0896665.main.ui.prompts.buttons.prompt_option_button import PromptOption
from com.github.dm0896665.main.ui.prompts.yes_no_prompt import YesNoPrompt
from com.github.dm0896665.main.ui.screen import Screen


class NewGame(Screen):
    def __init__(self):
        super().__init__("new_game")
        print("ello")

    def on_screen_will_show(self):
        print("I'll show....trust")

    def on_screen_did_show(self):
        print("I show.")
        results: PromptOption = YesNoPrompt("Do you want Maths?").show_and_get_results()
        print("Results:" + results.get_option_text)