unicodes = {
     'PL': {'Ą': 'A', 'Ę': 'E', 'Ó': 'O', 'Ł': 'L', 'Ń': 'N', 'Ź': 'Z', 'Ś': 'S'}
}
def generate(str, lang):
     for key, value in unicodes[lang].items():
          str = str.replace(key, value)
     return str