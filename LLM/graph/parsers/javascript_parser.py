import tree_sitter_javascript as tsjs
from tree_sitter import Language

from .typescript_parser import JsTsParser

JS_LANGUAGE = Language(tsjs.language())


class JavaScriptParser(JsTsParser):
    def __init__(self) -> None:
        super().__init__(JS_LANGUAGE)

    def _language_name(self) -> str:
        return "javascript"
