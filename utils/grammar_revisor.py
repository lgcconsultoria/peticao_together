import language_tool_python

class GrammarRevisor:
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('pt-BR')

    def revisar_texto(self, texto: str) -> str:
        """Revisa o texto para corrigir erros gramaticais e de ortografia.

        Args:
            texto: Texto a ser revisado.

        Returns:
            Texto revisado.
        """
        matches = self.tool.check(texto)
        return language_tool_python.utils.correct(texto, matches) 