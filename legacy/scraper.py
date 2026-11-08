#!/usr/bin/env python3
"""
Scraper robusto para WoWhead (expansão Midnight) usando Crawl4AI.
Extrai ferramentas de profissão, encantamentos e missivas com filtros de qualidade.
"""

import asyncio
import os
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig, LLMExtractionStrategy, LLMConfig

# Movido para `legacy/`: mantém a raiz do projeto no sys.path para `config`.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from runtime import configurar_event_loop_windows  # noqa: E402

# Importar configurações
try:
    from config import PROFESSION_TOOLS_URLS, ENCHANTMENT_URLS, MISSIVE_URLS
    from config import PROFESSION_TOOLS_SCHEMA, ENCHANTMENT_SCHEMA, MISSIVE_SCHEMA
    from config import LLM_PROVIDER
except ImportError:
    # Fallback se config.py não existir
    PROFESSION_TOOLS_URLS = []
    ENCHANTMENT_URLS = []
    MISSIVE_URLS = []
    PROFESSION_TOOLS_SCHEMA = {}
    ENCHANTMENT_SCHEMA = {}
    MISSIVE_SCHEMA = {}
    LLM_PROVIDER = "deepseek/deepseek-chat"

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class WowheadItem:
    """Estrutura para armazenar dados de itens do WoWhead."""
    id: str
    nome_ptbr: str
    tipo: str  # 'ferramenta_profissao', 'encantamento', 'missiva'
    profissao: Optional[str] = None
    atributos_secundarios: Optional[Dict[str, str]] = None
    atributo_conferido: Optional[str] = None
    valor: Optional[str] = None
    atributo_adicionado: Optional[str] = None
    valor_base: Optional[str] = None
    qualidade: Optional[int] = None
    item_level: Optional[int] = None
    bonus_ids: List[str] = None
    url: Optional[str] = None

    def __post_init__(self):
        if self.bonus_ids is None:
            self.bonus_ids = []

class WowheadScraper:
    """Scraper principal para WoWhead."""

    def __init__(self):
        self.base_url = os.getenv("WOWHEAD_BASE_URL", "https://www.wowhead.com")
        self.language = os.getenv("WOWHEAD_LANGUAGE", "pt")
        self.quality_rank = int(os.getenv("QUALITY_RANK", 5))
        self.rare_item_level = int(os.getenv("RARE_ITEM_LEVEL", 232))
        self.epic_item_level_min = int(os.getenv("EPIC_ITEM_LEVEL_MIN", 305))

        # Configurar o crawler
        self.browser_config = BrowserConfig(
            headless=os.getenv("CRAWL4AI_BROWSER_HEADLESS", "true").lower() == "true",
            enable_stealth=os.getenv("CRAWL4AI_MAGIC_MODE", "true").lower() == "true",
            verbose=False,
            browser_type="chromium"
        )

        # Configurar estratégia de extração com LLM
        self.llm_config = LLMConfig(
            provider=LLM_PROVIDER,
            api_token=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.1,
            max_tokens=2000
        )

        # Configurar schemas
        self.schemas = {
            "ferramenta_profissao": PROFESSION_TOOLS_SCHEMA,
            "encantamento": ENCHANTMENT_SCHEMA,
            "missiva": MISSIVE_SCHEMA
        }

        self.crawler = AsyncWebCrawler(config=self.browser_config)

    async def __aenter__(self):
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    def extract_item_id_from_url(self, url: str) -> Optional[str]:
        """Extrai o ID do item da URL do WoWhead."""
        # Padrões de URL do WoWhead: /item=12345 ou /item=12345&bonus=...
        match = re.search(r'/item=(\d+)', url)
        if match:
            return match.group(1)
        return None

    def extract_bonus_ids_from_url(self, url: str) -> List[str]:
        """Extrai todos os bonus IDs da URL."""
        bonus_ids = []

        # Extrair parâmetros do caminho (WoWhead usa formato /item=12345&bonus=... no caminho)
        # Encontrar tudo após 'item=' até o final ou próximo '#'
        match = re.search(r'item=\d+(.*?)(?:#|$)', url)
        if match:
            params_str = match.group(1)
            # Extrair parâmetros como &bonus=... &gems=... &ench=...
            param_pattern = r'&(bonus|gems|ench)=([^&]+)'
            for param_match in re.finditer(param_pattern, params_str):
                param_name = param_match.group(1)
                param_value = param_match.group(2)

                # Separar valores por : ou ,
                for id_val in re.split(r'[:,]', param_value):
                    if id_val and id_val.isdigit():
                        bonus_ids.append(id_val)

        return bonus_ids

    async def extract_profession_tools(self, urls: List[str]) -> List[WowheadItem]:
        """Extrai ferramentas de profissão das URLs fornecidas."""
        items = []

        for url in urls:
            print(f"Processando ferramentas de profissão: {url}")

            # Primeiro, extrair a tabela 'Accessories & Tools' usando seletores CSS
            css_selector = "table:has(caption:contains('Accessories & Tools'))"

            result = await self.crawler.arun(
                url=url,
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=self.llm_config,
                    instruction="""Extraia todos os itens da tabela 'Accessories & Tools'.
Para cada item, capture:
1. ID do item (do link)
2. Nome em português
3. Profissão (mineração, skinning, tailoring, etc.)
4. Atributos secundários e seus valores

Retorne como uma lista de objetos JSON com campos: id, nome_ptbr, profissao, atributos_secundarios."""
                )
            )

            if result.success and result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)
                    if isinstance(data, list):
                        for item_data in data:
                            # Verificar filtros de qualidade
                            if self._passes_quality_filters(item_data):
                                item = WowheadItem(
                                    id=item_data.get("id", ""),
                                    nome_ptbr=item_data.get("nome_ptbr", ""),
                                    tipo="ferramenta_profissao",
                                    profissao=item_data.get("profissao"),
                                    atributos_secundarios=item_data.get("atributos_secundarios"),
                                    url=url
                                )
                                items.append(item)
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON da URL: {url}")

        return items

    async def extract_enchantments(self, urls: List[str]) -> List[WowheadItem]:
        """Extrai encantamentos das URLs fornecidas."""
        items = []

        for url in urls:
            print(f"Processando encantamentos: {url}")

            result = await self.crawler.arun(
                url=url,
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=self.llm_config,
                    instruction="""Extraia informações de encantamentos.
Para cada encantamento, capture:
1. ID do item
2. Nome em português
3. Atributo conferido
4. Valor do atributo

Retorne como uma lista de objetos JSON com campos: id, nome_ptbr, atributo_conferido, valor."""
                )
            )

            if result.success and result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)
                    if isinstance(data, list):
                        for item_data in data:
                            item = WowheadItem(
                                id=item_data.get("id", ""),
                                nome_ptbr=item_data.get("nome_ptbr", ""),
                                tipo="encantamento",
                                atributo_conferido=item_data.get("atributo_conferido"),
                                valor=item_data.get("valor"),
                                url=url
                            )
                            items.append(item)
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON da URL: {url}")

        return items

    async def extract_missives(self, urls: List[str]) -> List[WowheadItem]:
        """Extrai missivas das URLs fornecidas."""
        items = []

        for url in urls:
            print(f"Processando missivas: {url}")

            result = await self.crawler.arun(
                url=url,
                extraction_strategy=LLMExtractionStrategy(
                    llm_config=self.llm_config,
                    instruction="""Extraia informações de missivas.
Para cada missiva, capture:
1. ID do item
2. Nome em português
3. Atributo adicionado
4. Valor base

Retorne como uma lista de objetos JSON com campos: id, nome_ptbr, atributo_adicionado, valor_base."""
                )
            )

            if result.success and result.extracted_content:
                try:
                    data = json.loads(result.extracted_content)
                    if isinstance(data, list):
                        for item_data in data:
                            item = WowheadItem(
                                id=item_data.get("id", ""),
                                nome_ptbr=item_data.get("nome_ptbr", ""),
                                tipo="missiva",
                                atributo_adicionado=item_data.get("atributo_adicionado"),
                                valor_base=item_data.get("valor_base"),
                                url=url
                            )
                            items.append(item)
                except json.JSONDecodeError:
                    print(f"Erro ao decodificar JSON da URL: {url}")

        return items

    def _passes_quality_filters(self, item_data: Dict[str, Any]) -> bool:
        """Aplica filtros de qualidade baseados nos requisitos."""
        # Verificar qualidade Rank 5
        qualidade = item_data.get("qualidade")
        if qualidade and int(qualidade) != self.quality_rank:
            return False

        # Verificar item level para raros/épicos
        item_level = item_data.get("item_level")
        if item_level:
            ilvl = int(item_level)
            # Se for raro (qualidade 3?), verificar ilvl 232
            # Se for épico (qualidade 4?), verificar ilvl > 250
            # Implementação simplificada - ajustar conforme necessário
            pass

        return True

    def handle_variations(self, base_item: WowheadItem, urls: List[str]) -> List[WowheadItem]:
        """Lida com variações de atributos que geram IDs diferentes."""
        variations = []

        for url in urls:
            item_id = self.extract_item_id_from_url(url)
            bonus_ids = self.extract_bonus_ids_from_url(url)

            if item_id:
                variation = WowheadItem(
                    id=item_id,
                    nome_ptbr=base_item.nome_ptbr,
                    tipo=base_item.tipo,
                    profissao=base_item.profissao,
                    atributos_secundarios=base_item.atributos_secundarios,
                    atributo_conferido=base_item.atributo_conferido,
                    valor=base_item.valor,
                    atributo_adicionado=base_item.atributo_adicionado,
                    valor_base=base_item.valor_base,
                    qualidade=base_item.qualidade,
                    item_level=base_item.item_level,
                    bonus_ids=bonus_ids,
                    url=url
                )
                variations.append(variation)

        return variations

    async def run_scraping(self):
        """Executa o scraping completo."""
        print("Iniciando scraping do WoWhead Midnight...")

        # URLs fornecidas (exemplos - substituir pelas reais)
        profession_urls = [
            "https://www.wowhead.com/pt/guide/midnight/professions/mining-overview-trainer-locations-ores-tools#accessories-tools",
            "https://www.wowhead.com/pt/guide/midnight/professions/skinning-overview-trainer-locations-hides-tracking-tools#accessories-tools",
            "https://www.wowhead.com/pt/guide/midnight/professions/tailoring-overview-trainer-locations-recipes-tools#accessories-tools"
        ]

        # URLs de encantamentos e missivas (serão fornecidas)
        enchantment_urls = []  # Preencher com URLs reais
        missive_urls = []      # Preencher com URLs reais

        all_items = []

        # Extrair ferramentas de profissão
        profession_items = await self.extract_profession_tools(profession_urls)
        all_items.extend(profession_items)
        print(f"Extraídas {len(profession_items)} ferramentas de profissão")

        # Extrair encantamentos
        if enchantment_urls:
            enchantment_items = await self.extract_enchantments(enchantment_urls)
            all_items.extend(enchantment_items)
            print(f"Extraídos {len(enchantment_items)} encantamentos")

        # Extrair missivas
        if missive_urls:
            missive_items = await self.extract_missives(missive_urls)
            all_items.extend(missive_items)
            print(f"Extraídas {len(missive_items)} missivas")

        # Salvar resultados
        await self.save_results(all_items)

        return all_items

    async def save_results(self, items: List[WowheadItem]):
        """Salva os resultados em arquivos JSON."""
        output_dir = os.getenv("OUTPUT_DIR", "./data")
        os.makedirs(output_dir, exist_ok=True)

        # Converter para dicionários
        items_dict = [asdict(item) for item in items]

        # Salvar por tipo
        for item_type in ["ferramenta_profissao", "encantamento", "missiva"]:
            type_items = [item for item in items_dict if item["tipo"] == item_type]
            if type_items:
                filename = os.path.join(output_dir, f"wowhead_{item_type}.json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(type_items, f, ensure_ascii=False, indent=2)
                print(f"Salvo {len(type_items)} itens do tipo '{item_type}' em {filename}")

        # Salvar todos os itens
        all_filename = os.path.join(output_dir, "wowhead_all_items.json")
        with open(all_filename, "w", encoding="utf-8") as f:
            json.dump(items_dict, f, ensure_ascii=False, indent=2)
        print(f"Salvo total de {len(items_dict)} itens em {all_filename}")

async def main():
    """Função principal."""
    print("=== Scraper WoWhead Midnight ===")
    print("Configurando ambiente...")

    # Verificar chave de API
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("ERRO: DEEPSEEK_API_KEY não configurada no arquivo .env")
        print("Por favor, adicione sua chave da API DeepSeek no arquivo .env")
        return

    async with WowheadScraper() as scraper:
        items = await scraper.run_scraping()
        print(f"\nScraping concluído! Total de itens extraídos: {len(items)}")

if __name__ == "__main__":
    # Workaround de event loop centralizado em `runtime.py`.
    configurar_event_loop_windows()
    asyncio.run(main())


