import sublime, sublime_plugin
import sys
sys.path.append('C:\\Users\\Marcelo\\AppData\\Roaming\\Sublime Text 3\\Packages\\User\\pyperclip-1.5.27.zip\\pyperclip-1.5.27')
import pyperclip
import re
import unicodedata
from collections import OrderedDict
# Extends TextCommand so that run() receives a View to modify.  

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                    if unicodedata.category(c) != 'Mn')

variavel ="""
      [--0:1--]-{1}
"""

TEXTO = "{0}"
RAPIDO = OrderedDict([
    ("include2", """{{% include2 \"[--0:0--]/{0}.html\" %}}"""),
    ("comentario", """<!-- [--0:0--] {0} -->"""),
    ("<p>", """<p>{0}</p>"""),
    ("ctrl+v", """{0}"""),
    ("variavel", variavel)
])


class MudaCommand(sublime_plugin.WindowCommand):

    def run(self, paran=None):
        self.window.show_input_panel("Padrão", TEXTO, self.on_done, self.on_change, None)

    def on_done(self, text):
        self.window.show_input_panel("Padrão", TEXTO, self.on_done, self.on_change, None)

    def on_change(self, text):
        global TEXTO
        TEXTO = text


def substituicoes(text):
    return [
        text,
        strip_accents(text.replace(" ","_").lower().replace(":","")),
        text.replace(":",""),
        ''.join(ch for ch in text if ch.isalnum() or ch == " ")
    ]

class DuplicateCommand(sublime_plugin.TextCommand):
    def run(self, edit):  
        for region in self.view.sel():  
            text = " ".join(re.split(r'[\r\n]+', pyperclip.paste().strip()))
            text = TEXTO.format(*substituicoes(text))
            self.view.replace(edit, region, text)


class RapidoCommand(sublime_plugin.WindowCommand):

    def run(self, paran=None):
        self.window.show_quick_panel(list(RAPIDO.keys()), self.on_done)

    def on_done(self, index):
        global TEXTO
        if index == -1:
            return
        self.selecionado = list(RAPIDO.values())[index]
        groups = re.findall(r"\[--(.*?):(.*?)--\]", self.selecionado)
        if groups:
            texto2 = self.selecionado.replace("{", "{{").replace("}", "}}")
            self.selecionado = re.sub(r"\[--(.*?):(.*?)--\]", r"{d[\1][\2]}", texto2)
            self.count = len({x[0] for x in groups})
            self.args = []

        if self.count:
            self.window.show_input_panel("Substituicao", "", self.on_done2, None, None)
        else:
            TEXTO = self.selecionado
            self.window.run_command("muda")

    def on_done2(self, text):
        global TEXTO
        self.count -= 1
        self.args.append(
            substituicoes(text)
        )
        if self.count:
            self.window.show_input_panel("Substituicao", "", self.on_done2, None, None)
        else:
            print(self.selecionado, self.args)
            TEXTO = self.selecionado.format(d=self.args)
            self.window.run_command("muda")
