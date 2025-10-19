class StringUtil:
    @staticmethod
    def bool_to_on_off_str(boolean: bool) -> str:
        return "on" if boolean else "off"

    @staticmethod
    def bool_to_on_off_str_capital(boolean: bool) -> str:
        return "On" if boolean else "Off"