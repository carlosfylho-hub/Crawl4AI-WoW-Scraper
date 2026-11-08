#!/usr/bin/env python3
"""
Cliente de tooltip do Wowhead (Season 2).

Consulta o endpoint público de tooltip por `item + bonus` para validar o
item level real de uma variante. É deliberadamente **tolerante a falhas**:
nunca levanta exceção que derrube o run — em qualquer erro retorna `None`
e registra `logging.debug`.

Cache:
    ``data/_cache/tooltips.json`` indexado por ``sha1(item|bonus|locale)``
    com TTL de 7 dias.
"""

from __future__ import annotations

import hashlib
import html
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

LOGGER = logging.getLogger(__name__)

TOOLTIP_URL = "https://nether.wowhead.com/tooltip/item/{item_id}"
CACHE_PATH_PADRAO = os.path.join("data", "_cache", "tooltips.json")
TTL_SEGUNDOS = 7 * 24 * 60 * 60
TIMEOUT_PADRAO = 8.0

#: User-Agent padrão (mesmo default usado pelo crawler em `coleta.py`).
USER_AGENT_PADRAO = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

#: Referer exigido pelo endpoint público de tooltip (F-04).
REFERER_PADRAO = "https://www.wowhead.com/"

#: Backoff exponencial entre tentativas (F-04): 2s, 4s, 8s.
ESPERAS_RETRY_PADRAO: Tuple[float, ...] = (2.0, 4.0, 8.0)

#: Tentativas totais = 1 chamada + 1 por espera de backoff.
MAX_TENTATIVAS = 1 + len(ESPERAS_RETRY_PADRAO)

_TRACK_RE = re.compile(
    r"\b(Hero|Myth|Mythic|Veteran|Champion|Explorer|Adventurer|"
    r"Her[oó]i|M[ií]tico|Veterano|Campe[aã]o|Explorador|Aventureiro)\b"
    r"[^\n]{0,24}",
    re.IGNORECASE,
)


# =============================================================================
# Utilidades
# =============================================================================

def _chave_cache(item_id: Any, bonus_ids: Optional[List[str]], locale: int) -> str:
    bonus = sorted(str(b) for b in (bonus_ids or []) if str(b))
    bruto = f"{item_id}|{':'.join(bonus)}|{locale}"
    return hashlib.sha1(bruto.encode("utf-8")).hexdigest()


def _para_int(valor: Any) -> int:
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return 0


def _texto_de_html(markup: str) -> str:
    """Remove tags de um fragmento HTML de tooltip e normaliza espaços."""
    if not markup:
        return ""
    texto = re.sub(r"<[^>]+>", "\n", str(markup))
    texto = html.unescape(texto)
    linhas = [linha.strip() for linha in texto.splitlines()]
    return "\n".join(linha for linha in linhas if linha)


def _extrair_track(texto: str) -> str:
    m = _TRACK_RE.search(texto or "")
    return re.sub(r"\s+", " ", m.group(0)).strip() if m else ""


def montar_url_tooltip(
    item_id: Any, bonus_ids: Optional[List[str]] = None, locale: int = 8
) -> str:
    """Monta a URL do endpoint de tooltip para `item + bonus`."""
    query: Dict[str, str] = {"dataEnv": "1", "locale": str(locale)}
    bonus = [str(b) for b in (bonus_ids or []) if str(b)]
    if bonus:
        query["bonus"] = ":".join(bonus)
    base = TOOLTIP_URL.format(item_id=item_id)
    # `safe=":"` mantém o separador de bonus exigido pelo Wowhead.
    return f"{base}?{urllib.parse.urlencode(query, safe=':')}"


#: Chaves do contrato público do tooltip (P-04). Entradas de cache antigas que
#: não contenham todas elas são ignoradas e refeitas.
CHAVES_CONTRATO_TOOLTIP = (
    "nome",
    "nome_ptbr",
    "nome_en",
    "item_level",
    "track_rotulo",
    "qualidade",
    "icone_url",
    "atributos_primarios",
    "atributos_secundarios",
    "bonus_ids",
    "tooltip_html",
    "tooltip_texto",
)


def _atributos_do_tooltip(texto: str) -> Tuple[Dict[str, int], Dict[str, int]]:
    """Extrai atributos do tooltip HTTP reutilizando o parser canônico."""
    try:
        from wow_season2 import extrair_atributos

        return extrair_atributos(texto or "")
    except Exception:  # noqa: BLE001 - degradação silenciosa
        LOGGER.debug("não foi possível extrair atributos do tooltip")
        return {}, {}


def _icone_do_tooltip(nome_icone: Any) -> str:
    """Monta a URL CDN a partir do campo `icon` do JSON de tooltip."""
    if not nome_icone:
        return ""
    try:
        from wow_season2 import montar_icone_url

        return montar_icone_url(str(nome_icone)) or ""
    except Exception:  # noqa: BLE001 - degradação silenciosa
        return ""


def _montar_saida(
    *,
    nome: str,
    item_level: int,
    track: str,
    qualidade: int,
    icone_url: str,
    primarios: Dict[str, int],
    secundarios: Dict[str, int],
    bonus: List[str],
    tooltip_html: str,
    tooltip_texto: str,
    locale: Optional[int],
) -> Dict[str, Any]:
    """Monta o contrato público do tooltip, separando nome PT-BR/EN."""
    eh_en = locale == 0
    return {
        "nome": nome,
        "nome_ptbr": "" if eh_en else nome,
        "nome_en": nome if eh_en else "",
        "item_level": item_level,
        "track_rotulo": track,
        "qualidade": qualidade,
        "icone_url": icone_url,
        "atributos_primarios": primarios,
        "atributos_secundarios": secundarios,
        "bonus_ids": list(bonus),
        "tooltip_html": tooltip_html,
        "tooltip_texto": tooltip_texto,
    }


def _interpretar_resposta(
    texto: str,
    bonus_ids: Optional[List[str]] = None,
    locale: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Interpreta o JSON (ou HTML) retornado pelo endpoint de tooltip.

    Contrato (P-04): ``nome``, ``nome_ptbr``, ``nome_en``, ``item_level``,
    ``track_rotulo``, ``qualidade``, ``icone_url``, ``atributos_primarios``,
    ``atributos_secundarios``, ``bonus_ids`` e ``tooltip_html``.
    """
    if not texto:
        return None

    bonus = [str(b) for b in (bonus_ids or []) if str(b)]

    dados = None
    try:
        dados = json.loads(texto)
    except (ValueError, TypeError):
        dados = None

    if not isinstance(dados, dict):
        # Fallback: alguns mirrors retornam o tooltip como HTML puro.
        texto_tooltip = _texto_de_html(texto)
        nivel = _extrair_ilvl_texto(texto_tooltip)
        if not nivel:
            return None
        primarios, secundarios = _atributos_do_tooltip(texto_tooltip)
        return _montar_saida(
            nome=texto_tooltip.splitlines()[0] if texto_tooltip else "",
            item_level=nivel,
            track=_extrair_track(texto_tooltip),
            qualidade=0,
            icone_url="",
            primarios=primarios,
            secundarios=secundarios,
            bonus=bonus,
            tooltip_html=texto,
            tooltip_texto=texto_tooltip,
            locale=locale,
        )

    nome = str(dados.get("name") or dados.get("nome") or "").strip()
    tooltip = str(dados.get("tooltip") or dados.get("html") or "")
    texto_tooltip = _texto_de_html(tooltip)

    item_level = _para_int(
        dados.get("itemLevel")
        or dados.get("item_level")
        or dados.get("ilvl")
        or dados.get("level")
    )
    if not item_level:
        item_level = _extrair_ilvl_texto(texto_tooltip)

    qualidade = _para_int(dados.get("quality") or dados.get("qualidade"))
    track = _extrair_track(texto_tooltip or nome)
    primarios, secundarios = _atributos_do_tooltip(texto_tooltip)
    icone_url = _icone_do_tooltip(dados.get("icon") or dados.get("iconUrl"))

    if not nome and not item_level:
        return None

    return _montar_saida(
        nome=nome,
        item_level=item_level,
        track=track,
        qualidade=qualidade,
        icone_url=icone_url,
        primarios=primarios,
        secundarios=secundarios,
        bonus=bonus,
        tooltip_html=tooltip,
        tooltip_texto=texto_tooltip,
        locale=locale,
    )


def _extrair_ilvl_texto(texto: str) -> int:
    padroes = (
        re.compile(r"item\s*level\s*[:.]?\s*(\d{2,4})", re.IGNORECASE),
        re.compile(
            r"n[ií]vel\s*(?:de|do)\s*item\s*[:.]?\s*(\d{2,4})", re.IGNORECASE
        ),
        re.compile(r"\bilvl\s*[=:]\s*(\d{2,4})", re.IGNORECASE),
    )
    for pat in padroes:
        m = pat.search(texto or "")
        if m:
            return _para_int(m.group(1))
    return 0


def _user_agent() -> str:
    """User-Agent efetivo (`CRAWL4AI_USER_AGENT` com fallback navegador real)."""
    valor = (os.getenv("CRAWL4AI_USER_AGENT") or "").strip()
    return valor or USER_AGENT_PADRAO


def _esperas_retry() -> Tuple[float, ...]:
    """Intervalos de backoff (default 2s/4s/8s; ajustável por env)."""
    bruto = (os.getenv("TOOLTIP_RETRY_BACKOFF") or "").strip()
    if not bruto:
        return ESPERAS_RETRY_PADRAO
    valores: List[float] = []
    for parte in bruto.split(","):
        try:
            valor = float(parte.strip())
        except (TypeError, ValueError):
            LOGGER.debug("TOOLTIP_RETRY_BACKOFF inválido: %r", bruto)
            return ESPERAS_RETRY_PADRAO
        if valor < 0:
            return ESPERAS_RETRY_PADRAO
        valores.append(valor)
    return tuple(valores) or ESPERAS_RETRY_PADRAO


def _fetch_urllib(url: str, timeout: float) -> str:
    """GET simples via urllib (sem dependências extras)."""
    requisicao = urllib.request.Request(
        url,
        headers={
            "User-Agent": _user_agent(),
            "Referer": REFERER_PADRAO,
            "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(requisicao, timeout=timeout) as resposta:
        return resposta.read().decode("utf-8", errors="replace")


# =============================================================================
# Cache em disco
# =============================================================================

class TooltipCache:
    """Cache em JSON indexado por `sha1(item|bonus|locale)` com TTL."""

    def __init__(self, caminho: str = CACHE_PATH_PADRAO, ttl: int = TTL_SEGUNDOS):
        self.caminho = caminho
        self.ttl = int(ttl or 0)
        self._dados: Optional[Dict[str, Any]] = None

    def _carregar(self) -> Dict[str, Any]:
        if self._dados is not None:
            return self._dados
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
            self._dados = conteudo if isinstance(conteudo, dict) else {}
        except (OSError, ValueError):
            self._dados = {}
        return self._dados

    def obter(
        self, item_id: Any, bonus_ids: Optional[List[str]], locale: int = 8
    ) -> Optional[Dict[str, Any]]:
        dados = self._carregar()
        entrada = dados.get(_chave_cache(item_id, bonus_ids, locale))
        if not isinstance(entrada, dict):
            return None
        ts = float(entrada.get("ts") or 0)
        if self.ttl and (time.time() - ts) > self.ttl:
            return None
        valor = entrada.get("dados")
        return valor if isinstance(valor, dict) else None

    def gravar(
        self,
        item_id: Any,
        bonus_ids: Optional[List[str]],
        valor: Dict[str, Any],
        locale: int = 8,
    ) -> None:
        dados = self._carregar()
        dados[_chave_cache(item_id, bonus_ids, locale)] = {
            "ts": time.time(),
            "dados": valor,
        }
        self._salvar()

    def _salvar(self) -> None:
        try:
            diretorio = os.path.dirname(self.caminho)
            if diretorio:
                os.makedirs(diretorio, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as f:
                json.dump(self._dados or {}, f, ensure_ascii=False, indent=2)
        except OSError as exc:  # pragma: no cover - falha de escrita é tolerada
            LOGGER.debug("não foi possível salvar cache de tooltips: %s", exc)


_CACHE_GLOBAL: Optional[TooltipCache] = None


def _cache_padrao() -> TooltipCache:
    global _CACHE_GLOBAL
    if _CACHE_GLOBAL is None:
        _CACHE_GLOBAL = TooltipCache()
    return _CACHE_GLOBAL


# =============================================================================
# API pública
# =============================================================================

def consultar_tooltip(
    item_id: Any,
    bonus_ids: Optional[List[str]] = None,
    locale: int = 8,
    cache: Optional[TooltipCache] = None,
    fetch: Any = None,
    timeout: float = TIMEOUT_PADRAO,
) -> Optional[Dict[str, Any]]:
    """
    Consulta o tooltip de `item + bonus`.

    Retorna o contrato de :data:`CHAVES_CONTRATO_TOOLTIP`
    (``nome``, ``nome_ptbr``, ``nome_en``, ``item_level``, ``track_rotulo``,
    ``qualidade``, ``icone_url``, ``atributos_primarios``,
    ``atributos_secundarios``, ``bonus_ids`` e ``tooltip_html``) ou ``None``.
    Nunca levanta exceção. `fetch` e `cache` são injetáveis para testes
    offline.
    """
    try:
        ident = str(item_id or "").strip()
        if not ident.isdigit():
            return None

        cache_ativo = cache if cache is not None else _cache_padrao()
        em_cache = cache_ativo.obter(ident, bonus_ids, locale)
        if em_cache is not None and all(
            chave in em_cache for chave in CHAVES_CONTRATO_TOOLTIP
        ):
            return em_cache

        fonte = fetch or _fetch_urllib
        url = montar_url_tooltip(ident, bonus_ids, locale)
        esperas = _esperas_retry()
        tentativas = len(esperas) + 1
        texto = ""
        for tentativa in range(tentativas):
            try:
                texto = fonte(url, timeout)
                if texto:
                    break
            except Exception as exc:  # noqa: BLE001 - tooltip nunca derruba o run
                LOGGER.debug(
                    "tooltip falhou (tentativa %s/%s) item=%s: %s",
                    tentativa + 1,
                    tentativas,
                    ident,
                    exc,
                )
                texto = ""
            # Backoff exponencial 2s/4s/8s (F-04), nunca levanta exceção.
            if tentativa < len(esperas):
                espera = esperas[tentativa]
                LOGGER.debug(
                    "tooltip aguardando %.1fs antes da tentativa %s item=%s",
                    espera,
                    tentativa + 2,
                    ident,
                )
                time.sleep(espera)

        if not texto:
            return None

        dados = _interpretar_resposta(texto, bonus_ids, locale)
        if not dados:
            return None

        cache_ativo.gravar(ident, bonus_ids, dados, locale)
        return dados
    except Exception as exc:  # noqa: BLE001 - degradação silenciosa
        LOGGER.debug("consultar_tooltip ignorou erro item=%s: %s", item_id, exc)
        return None
