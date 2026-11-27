class ErroApresentacao(Exception):
    """Erro de conteúdo/estrutura: a montagem para e mostra onde está o problema."""


class Campos:
    """Validação estrita de um dicionário do YAML: campos obrigatórios, opcionais e desconhecidos."""

    def __init__(self, d, onde: str, obrig=(), opc=()):
        if not isinstance(d, dict):
            raise ErroApresentacao(f"{onde}: esperado um bloco com campos, recebido {type(d).__name__}: {d!r}")
        faltam = [c for c in obrig if c not in d]
        sobram = sorted(set(d) - set(obrig) - set(opc))
        if faltam:
            raise ErroApresentacao(f"{onde}: falta o campo {', '.join(faltam)}")
        if sobram:
            validos = ", ".join(list(obrig) + list(opc))
            raise ErroApresentacao(f"{onde}: campo desconhecido {', '.join(sobram)} (válidos: {validos})")
        self.d, self.onde = d, onde

    def __getitem__(self, k):
        return self.d[k]

    def get(self, k, padrao=None):
        return self.d.get(k, padrao)

    def lista(self, k, padrao=None):
        v = self.d.get(k, padrao)
        if v is None:
            return []
        if not isinstance(v, list):
            raise ErroApresentacao(f"{self.onde}.{k}: esperado uma lista")
        return v
