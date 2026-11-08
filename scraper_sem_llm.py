#!/usr/bin/env python3
"""
Scraper WoWhead Midnight sem LLM.

Adapter fino sobre os parsers canônicos de `wow_season2.py` (via `coleta.py`).
NÃO usa `JsonCssExtractionStrategy`/`css_selectors` (removidos na API 0.8.6).
Não requer API do DeepSeek ou qualquer LLM.
"""

import os
import json
import asyncio
import re
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime

# F-09: stdout/stderr em UTF-8 no console do Windows, antes dos imports
# pesados (crawl4ai/playwright).
import runtime as _runtime  # noqa: F401

from crawl4ai import AsyncWebCrawler, BrowserConfig

from coleta import extrair_itens_de_url
from tooltip_raidbots import montar_tooltip_raidbots


logger = logging.getLogger("scraper_sem_llm")

# Logging padrão: garante traceback visível mesmo quando chamado por script.
# (Os `print` de progresso continuam existindo; isto é para falhas.)
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

try:
    from config import (
        PARTE1_URLS, PARTE2_URLS, PARTE3_URLS, PARTE4_URLS, PARTE5_URLS,
        ILVL_PISO_PADRAO, ILVL_TETO_PADRAO, QUALIDADE_MINIMA_PADRAO,
    )
except ImportError as e:
    print(f"Erro ao importar config: {e}")
    print("Certifique-se de que config.py existe no mesmo diretório")
    exit(1)


@dataclass
class FerramentaProducao:
    """Representa uma ferramenta de produção (Partes 1-3)."""
    id_item_completo: str
    nome_ptbr: str
    profissao: str
    qualidade: str
    item_level: int
    rank: int
    atributo_tipo: str
    atributo_valor: int
    bonus_ids: List[str]
    url: str
    # P-06/F-08: campos opcionais (compatíveis com o contrato `asdict`).
    icone: str = ""
    nome_en: str = ""
    atributos_primarios: Dict[str, int] = field(default_factory=dict)
    atributos_secundarios: Dict[str, int] = field(default_factory=dict)
    tooltip_raidbots: str = ""


@dataclass
class EncantamentoFerramenta:
    """Representa um encantamento de ferramenta (Parte 4)."""
    id_item_completo: str
    nome_ptbr: str
    profissao: str
    qualidade: str
    item_level: int
    rank: int
    atributo_tipo: str
    atributo_valor: int
    bonus_ids: List[str]
    url: str
    # P-06/F-08: campos opcionais (compatíveis com o contrato `asdict`).
    icone: str = ""
    nome_en: str = ""
    atributos_primarios: Dict[str, int] = field(default_factory=dict)
    atributos_secundarios: Dict[str, int] = field(default_factory=dict)
    tooltip_raidbots: str = ""


@dataclass
class MissivaProfissao:
    """Representa uma missiva talassiana (Parte 5)."""
    id_item_completo: str
    nome_ptbr: str
    profissao: str
    qualidade: str
    item_level: int
    rank: int
    atributo_tipo: str
    atributo_valor: int
    bonus_ids: List[str]
    url: str
    # P-06/F-08: campos opcionais (compatíveis com o contrato `asdict`).
    icone: str = ""
    nome_en: str = ""
    atributos_primarios: Dict[str, int] = field(default_factory=dict)
    atributos_secundarios: Dict[str, int] = field(default_factory=dict)
    tooltip_raidbots: str = ""


# =============================================================================
# Conversão dict (canônico) -> dataclasses existentes
# =============================================================================

def _para_int(valor: Any) -> int:
    """Converte valores do parser ("+1.234", 30, "30") em int sem estourar."""
    if isinstance(valor, bool):
        return int(valor)
    if isinstance(valor, (int, float)):
        return int(valor)
    texto = re.sub(r"[^\d]", "", str(valor or ""))
    return int(texto) if texto else 0


def _nome_item(conteudo: Dict[str, Any]) -> str:
    return str(
        conteudo.get("nome_ptbr") or conteudo.get("nome") or ""
    ).strip()


def _qualidade_str(conteudo: Dict[str, Any]) -> str:
    nome = conteudo.get("qualidade_nome")
    if nome:
        return str(nome)
    qualidade = _para_int(conteudo.get("qualidade"))
    return str(qualidade) if qualidade else ""


def _id_completo(conteudo: Dict[str, Any]) -> str:
    ident = conteudo.get("id_completo")
    if ident:
        return str(ident)
    item_id = conteudo.get("id") or ""
    bonus = conteudo.get("bonus_ids") or []
    if bonus:
        return f"item={item_id}&bonus={':'.join(str(b) for b in bonus)}"
    return f"item={item_id}" if item_id else ""


def _atributo_principal(conteudo: Dict[str, Any]) -> tuple:
    """Primeiro atributo disponível (secundário tem prioridade)."""
    for chave in ("atributos_secundarios", "atributos_primarios"):
        mapa = conteudo.get(chave) or {}
        if isinstance(mapa, dict) and mapa:
            nome = next(iter(mapa))
            return str(nome), _para_int(mapa[nome])
    return "", 0


def _icone(conteudo: Dict[str, Any]) -> str:
    """URL do ícone canônico (`icone_url`), com fallback para `icone`."""
    return str(conteudo.get("icone_url") or conteudo.get("icone") or "").strip()


def _tooltip_raidbots(conteudo: Dict[str, Any]) -> str:
    """Tooltip Raidbots do dict canônico; nunca levanta exceção."""
    existente = str(conteudo.get("tooltip_raidbots") or "").strip()
    if existente:
        return existente
    try:
        return montar_tooltip_raidbots(conteudo)
    except Exception:  # noqa: BLE001 - adapter nunca quebra por tooltip
        return ""


def _profissao_por_nome(nome: str, padrao: str = "Desconhecida") -> str:
    """Inferência de profissão por palavra-chave do nome (legado preservado)."""
    baixo = (nome or "").lower()
    regras = (
        ("engenhosidade", "Engenharia"),
        ("multicriação", "Escrivania"),
        ("multicriacao", "Escrivania"),
        ("finesse", "Escrivania"),
        ("destreza", "Ferraria"),
        ("percepção", "Mineração"),
        ("percepcao", "Mineração"),
        ("desenvoltura", "Esfolamento"),
    )
    for chave, profissao in regras:
        if chave in baixo:
            return profissao
    return padrao


def dict_para_ferramenta(
    conteudo: Dict[str, Any], url: str = "", profissao: str = ""
) -> FerramentaProducao:
    """Converte um dict canônico em `FerramentaProducao`."""
    atributo_tipo, atributo_valor = _atributo_principal(conteudo)
    return FerramentaProducao(
        id_item_completo=_id_completo(conteudo),
        nome_ptbr=_nome_item(conteudo),
        profissao=(
            conteudo.get("profissao_craft") or profissao or "Desconhecida"
        ),
        qualidade=_qualidade_str(conteudo),
        item_level=_para_int(conteudo.get("item_level")),
        rank=_para_int(conteudo.get("rank")) or 5,
        atributo_tipo=atributo_tipo,
        atributo_valor=atributo_valor,
        bonus_ids=[str(b) for b in (conteudo.get("bonus_ids") or [])],
        url=conteudo.get("url") or url,
        icone=_icone(conteudo),
        nome_en=str(conteudo.get("nome_en") or ""),
        atributos_primarios=dict(conteudo.get("atributos_primarios") or {}),
        atributos_secundarios=dict(conteudo.get("atributos_secundarios") or {}),
        tooltip_raidbots=_tooltip_raidbots(conteudo),
    )


def dict_para_encantamento(
    conteudo: Dict[str, Any], url: str = "", profissao: str = ""
) -> EncantamentoFerramenta:
    """Converte um dict canônico em `EncantamentoFerramenta`."""
    nome = _nome_item(conteudo)
    atributo_tipo, atributo_valor = _atributo_principal(conteudo)
    return EncantamentoFerramenta(
        id_item_completo=_id_completo(conteudo),
        nome_ptbr=nome,
        profissao=(
            conteudo.get("profissao_craft")
            or profissao
            or _profissao_por_nome(nome, "Encantamento")
        ),
        qualidade=_qualidade_str(conteudo),
        item_level=_para_int(conteudo.get("item_level")),
        rank=_para_int(conteudo.get("rank")) or 2,
        atributo_tipo=atributo_tipo,
        atributo_valor=atributo_valor,
        bonus_ids=[str(b) for b in (conteudo.get("bonus_ids") or [])],
        url=conteudo.get("url") or url,
        icone=_icone(conteudo),
        nome_en=str(conteudo.get("nome_en") or ""),
        atributos_primarios=dict(conteudo.get("atributos_primarios") or {}),
        atributos_secundarios=dict(conteudo.get("atributos_secundarios") or {}),
        tooltip_raidbots=_tooltip_raidbots(conteudo),
    )


def dict_para_missiva(
    conteudo: Dict[str, Any], url: str = "", profissao: str = ""
) -> MissivaProfissao:
    """Converte um dict canônico em `MissivaProfissao`."""
    nome = _nome_item(conteudo)
    atributo_tipo, atributo_valor = _atributo_principal(conteudo)
    return MissivaProfissao(
        id_item_completo=_id_completo(conteudo),
        nome_ptbr=nome,
        profissao=(
            conteudo.get("profissao_craft")
            or profissao
            or _profissao_por_nome(nome, "Desconhecida")
        ),
        qualidade=_qualidade_str(conteudo),
        item_level=_para_int(conteudo.get("item_level")),
        rank=_para_int(conteudo.get("rank")) or 1,
        atributo_tipo=atributo_tipo,
        atributo_valor=atributo_valor,
        bonus_ids=[str(b) for b in (conteudo.get("bonus_ids") or [])],
        url=conteudo.get("url") or url,
        icone=_icone(conteudo),
        nome_en=str(conteudo.get("nome_en") or ""),
        atributos_primarios=dict(conteudo.get("atributos_primarios") or {}),
        atributos_secundarios=dict(conteudo.get("atributos_secundarios") or {}),
        tooltip_raidbots=_tooltip_raidbots(conteudo),
    )


class WowheadScraperSemLLM:
    """Adapter sem LLM sobre os parsers canônicos (todas as 5 partes)."""

    def __init__(self, progress_callback=None):
        self.base_url = os.getenv("WOWHEAD_BASE_URL", "https://www.wowhead.com")
        self.quality_rank = int(os.getenv("QUALITY_RANK", 5))
        self.qualidade_min = int(
            os.getenv("QUALIDADE_MIN", QUALIDADE_MINIMA_PADRAO)
        )
        # Season 2: abandona as travas antigas (piso 250 / teto 300)
        self.ilvl_min = int(os.getenv("ILVL_MIN", ILVL_PISO_PADRAO))
        self.ilvl_max = int(os.getenv("ILVL_MAX", ILVL_TETO_PADRAO))
        self.rare_item_level = int(os.getenv("RARE_ITEM_LEVEL", self.ilvl_min))
        self.epic_item_level_min = int(
            os.getenv("EPIC_ITEM_LEVEL_MIN", self.ilvl_min)
        )
        self.progress_callback = progress_callback
        # Contador de erros por parte: {"parte1": [{"url","tipo","mensagem"}], ...}
        self.erros: Dict[str, List[Dict[str, Any]]] = {}

        # Configurar o crawler (apenas transporte de HTML; sem extração CSS)
        self.browser_config = BrowserConfig(
            headless=os.getenv("CRAWL4AI_BROWSER_HEADLESS", "true").lower()
            == "true",
            enable_stealth=os.getenv("CRAWL4AI_MAGIC_MODE", "true").lower()
            == "true",
            verbose=False,
            browser_type="chromium",
            viewport_width=1920,
            viewport_height=1080,
        )

        self.crawler = AsyncWebCrawler(config=self.browser_config)

    def _update_progress(
        self,
        message: str,
        current: Optional[int] = None,
        total: Optional[int] = None,
    ):
        """Atualiza o progresso se houver callback."""
        if self.progress_callback:
            self.progress_callback(message, current, total)

    def _registrar_erro(
        self, parte_num: int, url: Optional[str], exc: BaseException
    ) -> None:
        """Registra uma falha não fatal da parte para o resumo final."""
        chave = f"parte{parte_num}"
        self.erros.setdefault(chave, []).append(
            {
                "url": url or "",
                "tipo": type(exc).__name__,
                "mensagem": str(exc),
            }
        )

    def _resumo_erros(self) -> Dict[str, int]:
        """Quantidade de erros por parte (só as partes que falharam)."""
        return {chave: len(lista) for chave, lista in sorted(self.erros.items())}

    def _total_erros(self) -> int:
        """Total de erros registrados em todas as partes."""
        return sum(len(lista) for lista in self.erros.values())

    async def __aenter__(self):
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    def extract_item_id_from_url(self, url: str) -> str:
        """Extrai o ID do item da URL do WoWhead."""
        # Padrão: /pt/item=123456/nome-do-item
        match = re.search(r'/item=(\d+)', url)
        if match:
            return match.group(1)
        return ""

    def extract_bonus_ids_from_url(self, url: str) -> List[str]:
        """Extrai bonus IDs da URL do WoWhead."""
        # Padrão: &bonus=123:456:789
        match = re.search(r'&bonus=([\d:]+)', url)
        if match:
            return match.group(1).split(':')
        return []

    def get_profession_from_url(self, url: str) -> str:
        """Determina a profissão baseada na URL."""
        profession_map = {
            "alchemy": "Alquimia",
            "blacksmithing": "Ferraria",
            "cooking": "Culinária",
            "enchanting": "Encantamento",
            "engineering": "Engenharia",
            "fishing": "Pesca",
            "herbalism": "Herborismo",
            "inscription": "Escrivania",
            "jewelcrafting": "Joalheria",
            "leatherworking": "Couraria",
            "mining": "Mineração",
            "skinning": "Esfolamento",
            "tailoring": "Alfaiataria"
        }

        for key, value in profession_map.items():
            if key in url.lower():
                return value
        return "Desconhecida"

    def _passa_filtros_dict(self, conteudo: Dict[str, Any]) -> bool:
        """Filtros de qualidade/ilvl aplicados ao dict canônico."""
        qualidade = _para_int(conteudo.get("qualidade"))
        if self.qualidade_min and qualidade and qualidade < self.qualidade_min:
            return False

        ilvl = _para_int(conteudo.get("item_level"))
        if ilvl and (ilvl < self.ilvl_min or ilvl > self.ilvl_max):
            return False

        # Rank só é aplicado quando o tooltip realmente informou um rank.
        rank = _para_int(conteudo.get("rank"))
        if rank and self.quality_rank and rank != self.quality_rank:
            return False
        return True

    def _passa_filtros_qualidade(self, item: FerramentaProducao) -> bool:
        """
        Compatibilidade: aplica filtros de qualidade/ilvl em uma ferramenta.

        A faixa é controlada por ILVL_MIN/ILVL_MAX (padrão 305-350),
        eliminando as travas antigas de Raro 232 / Épico >250.
        """
        ilvl = int(item.item_level or 0)
        if ilvl and (ilvl < self.ilvl_min or ilvl > self.ilvl_max):
            return False
        if item.rank and self.quality_rank and item.rank != self.quality_rank:
            return False
        return True

    async def _coletar_parte(
        self,
        urls: List[str],
        parte_num: int,
        categoria: str,
        conversor,
        aplicar_filtros: bool,
    ) -> List[Any]:
        """
        Coleta e converte uma parte usando os parsers canônicos.

        Erros de configuração (`TypeError`/`AttributeError`/`ImportError`)
        propagam (exit != 0). Demais falhas são registradas em `self.erros`.
        """
        items: List[Any] = []
        total_urls = len(urls)

        for i, url in enumerate(urls, 1):
            self._update_progress(
                f"Parte {parte_num}: Processando URL {i}/{total_urls}",
                i,
                total_urls,
            )
            print(f"[Parte {parte_num}] Processando: {url}")

            profissao = self.get_profession_from_url(url)
            try:
                brutos = await extrair_itens_de_url(
                    url, categoria=categoria, crawler=self.crawler
                )
            except (TypeError, AttributeError, ImportError):
                # Erro de configuração/API: propaga até o main (exit != 0).
                logging.exception(
                    "Parte %s: erro de configuração ao processar %s. "
                    "Consulte docs/UPGRADE_CRAWL4AI.md",
                    parte_num,
                    url,
                )
                raise
            except Exception as e:
                logging.exception(
                    "Parte %s: erro ao processar URL %s", parte_num, url
                )
                self._registrar_erro(parte_num, url, e)
                continue

            if not brutos:
                logging.warning(
                    "Parte %s: nenhum item extraído de %s", parte_num, url
                )
                continue

            for conteudo in brutos:
                if aplicar_filtros and not self._passa_filtros_dict(conteudo):
                    print(
                        "  [FILTRADO] Item: %s (ILvl: %s, Qualidade: %s)"
                        % (
                            _nome_item(conteudo),
                            conteudo.get("item_level"),
                            conteudo.get("qualidade"),
                        )
                    )
                    continue
                item = conversor(conteudo, url=url, profissao=profissao)
                items.append(item)
                print(
                    f"  [OK] Item extraído: {item.nome_ptbr} "
                    f"(ILvl: {item.item_level}, Qualidade: {item.qualidade})"
                )

        return items

    async def extrair_ferramentas_parte(
        self, urls: List[str], parte_num: int
    ) -> List[FerramentaProducao]:
        """Extrai ferramentas de produção usando os parsers canônicos."""
        return await self._coletar_parte(
            urls,
            parte_num,
            categoria="ferramentas_profissao",
            conversor=dict_para_ferramenta,
            aplicar_filtros=True,
        )

    async def extrair_encantamentos(self) -> List[EncantamentoFerramenta]:
        """Extrai encantamentos de ferramenta (Parte 4)."""
        return await self._coletar_parte(
            PARTE4_URLS,
            4,
            categoria="encantamentos",
            conversor=dict_para_encantamento,
            aplicar_filtros=False,
        )

    async def extrair_missivas(self) -> List[MissivaProfissao]:
        """Extrai missivas talassianas (Parte 5)."""
        return await self._coletar_parte(
            PARTE5_URLS,
            5,
            categoria="missivas",
            conversor=dict_para_missiva,
            aplicar_filtros=False,
        )

    async def executar_scraping_completo(self):
        """Executa o scraping completo de todas as 5 partes."""
        self._update_progress("Iniciando scraping completo...", 0, 100)
        print("=" * 60)
        print("INICIANDO SCRAPING COMPLETO SEM LLM")
        print("(parsers canônicos — sem JsonCssExtractionStrategy)")
        print("=" * 60)

        # Zera o contador de erros desta execução
        self.erros.clear()

        resultados = {
            "parte1_ferramentas_producao": [],
            "parte2_ferramentas_coleta": [],
            "parte3_ferramentas_restante": [],
            "parte4_encantamentos": [],
            "parte5_missivas": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "versao_scraper": "1.1.0-sem-llm",
                "total_itens": 0,
                # Contador de falhas por parte (erro de configuração => exceção,
                # os demais erros ficam registrados aqui).
                "erros_por_parte": {},
                "total_erros": 0
            }
        }

        # Parte 1: Ferramentas de Produção
        self._update_progress("Parte 1: Ferramentas de Produção...", 10, 100)
        print("\n[PARTE 1] Extraindo ferramentas de produção...")
        parte1_items = await self.extrair_ferramentas_parte(PARTE1_URLS, 1)
        resultados["parte1_ferramentas_producao"] = [asdict(item) for item in parte1_items]
        print(f"  Extraídos: {len(parte1_items)} itens")

        # Parte 2: Ferramentas de Coleta e Joalheria
        self._update_progress("Parte 2: Ferramentas de Coleta e Joalheria...", 30, 100)
        print("\n[PARTE 2] Extraindo ferramentas de coleta e joalheria...")
        parte2_items = await self.extrair_ferramentas_parte(PARTE2_URLS, 2)
        resultados["parte2_ferramentas_coleta"] = [asdict(item) for item in parte2_items]
        print(f"  Extraídos: {len(parte2_items)} itens")

        # Parte 3: Restante das Profissões
        self._update_progress("Parte 3: Restante das Profissões...", 50, 100)
        print("\n[PARTE 3] Extraindo ferramentas das profissões restantes...")
        parte3_items = await self.extrair_ferramentas_parte(PARTE3_URLS, 3)
        resultados["parte3_ferramentas_restante"] = [asdict(item) for item in parte3_items]
        print(f"  Extraídos: {len(parte3_items)} itens")

        # Parte 4: Encantamentos de Ferramenta
        self._update_progress("Parte 4: Encantamentos de Ferramenta...", 70, 100)
        print("\n[PARTE 4] Extraindo encantamentos de ferramenta...")
        parte4_items = await self.extrair_encantamentos()
        resultados["parte4_encantamentos"] = [asdict(item) for item in parte4_items]
        print(f"  Extraídos: {len(parte4_items)} encantamentos")

        # Parte 5: Missivas Talassianas
        self._update_progress("Parte 5: Missivas Talassianas...", 90, 100)
        print("\n[PARTE 5] Extraindo missivas talassianas...")
        parte5_items = await self.extrair_missivas()
        resultados["parte5_missivas"] = [asdict(item) for item in parte5_items]
        print(f"  Extraídos: {len(parte5_items)} missivas")

        self._update_progress("Scraping completo concluído!", 100, 100)

        # Calcular total
        total = (
            len(parte1_items) + len(parte2_items) + len(parte3_items) +
            len(parte4_items) + len(parte5_items)
        )
        resultados["metadata"]["total_itens"] = total

        # Resumo de erros por parte (não fatal: apenas reportado)
        resultados["metadata"]["erros_por_parte"] = self._resumo_erros()
        resultados["metadata"]["total_erros"] = self._total_erros()

        if self._total_erros():
            logging.warning(
                "Scraping concluído com %s erro(s) registrados: %s",
                self._total_erros(),
                self._resumo_erros(),
            )

        print("\n" + "=" * 60)
        print(f"SCRAPING COMPLETADO: {total} itens extraídos")
        if self._total_erros():
            print(f"ERROS REGISTRADOS: {self._total_erros()} -> {self._resumo_erros()}")
        print("=" * 60)

        return resultados

    async def salvar_resultados_completos(self, resultados: Dict[str, Any]):
        """Salva os resultados completos em arquivos JSON.

        F-11: após gravar cada artefato timestamped, aplica a política de
        retenção (`_rotacionar_artefatos`) para que ``data/`` não acumule
        duplicados entre execuções.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Import tardio evita custo/ciclo de import no topo do módulo.
        from scraper_season2 import rotacionar_artefatos

        # Criar diretório data se não existir
        os.makedirs("data", exist_ok=True)

        # Salvar resultados completos
        arquivo_completo = f"data/wowhead_all_items_sem_llm_{timestamp}.json"
        with open(arquivo_completo, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        rotacionar_artefatos("wowhead_all_items_sem_llm_*.json")
        print(f"[OK] Resultados completos salvos em: {arquivo_completo}")

        # Salvar por partes
        if resultados["parte1_ferramentas_producao"]:
            arquivo_parte1 = f"data/wowhead_ferramenta_profissao_sem_llm_{timestamp}.json"
            with open(arquivo_parte1, "w", encoding="utf-8") as f:
                json.dump(resultados["parte1_ferramentas_producao"], f, ensure_ascii=False, indent=2)
            rotacionar_artefatos("wowhead_ferramenta_profissao_sem_llm_*.json")

        if resultados["parte4_encantamentos"]:
            arquivo_parte4 = f"data/wowhead_encantamento_sem_llm_{timestamp}.json"
            with open(arquivo_parte4, "w", encoding="utf-8") as f:
                json.dump(resultados["parte4_encantamentos"], f, ensure_ascii=False, indent=2)
            rotacionar_artefatos("wowhead_encantamento_sem_llm_*.json")

        if resultados["parte5_missivas"]:
            arquivo_parte5 = f"data/wowhead_missiva_sem_llm_{timestamp}.json"
            with open(arquivo_parte5, "w", encoding="utf-8") as f:
                json.dump(resultados["parte5_missivas"], f, ensure_ascii=False, indent=2)
            rotacionar_artefatos("wowhead_missiva_sem_llm_*.json")

        return arquivo_completo


async def main():
    """Função principal para executar o scraper sem LLM."""
    print("Scraper WoWhead Midnight - Versão Sem LLM")
    print("Usando parsers canônicos do projeto (não requer API DeepSeek)")
    print("-" * 60)

    async with WowheadScraperSemLLM() as scraper:
        resultados = await scraper.executar_scraping_completo()
        arquivo_salvo = await scraper.salvar_resultados_completos(resultados)

        print("\n[OK] Scraping concluído com sucesso!")
        print(f"[OK] Arquivo principal salvo: {arquivo_salvo}")
        print(f"[OK] Total de itens: {resultados['metadata']['total_itens']}")
        print(f"[OK] Erros por parte: {resultados['metadata']['erros_por_parte']}")


if __name__ == "__main__":
    asyncio.run(main())
