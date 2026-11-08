#!/usr/bin/env python3
"""
Scraper completo para WoWhead Midnight - Todas as 5 partes.
Implementa extração específica para cada grupo de URLs com schemas detalhados.
"""

import asyncio
import os
import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig, LLMExtractionStrategy, LLMConfig

# Movido para `legacy/`: mantém a raiz do projeto no sys.path para `config`.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

# Importar configurações
try:
    from config import (
        PARTE1_URLS, PARTE2_URLS, PARTE3_URLS, PARTE4_URLS, PARTE5_URLS,
        FERRAMENTAS_PRODUCAO_SCHEMA, ENCANTAMENTOS_FERRAMENTA_SCHEMA,
        MISSIVAS_PROFISSOES_SCHEMA, ILVL_PISO_PADRAO, ILVL_TETO_PADRAO,
        LLM_PROVIDER
    )
except ImportError:
    # Fallback se config.py não existir
    PARTE1_URLS = PARTE2_URLS = PARTE3_URLS = PARTE4_URLS = PARTE5_URLS = []
    FERRAMENTAS_PRODUCAO_SCHEMA = {}
    ENCANTAMENTOS_FERRAMENTA_SCHEMA = {}
    MISSIVAS_PROFISSOES_SCHEMA = {}
    ILVL_PISO_PADRAO = 305
    ILVL_TETO_PADRAO = 350
    LLM_PROVIDER = "deepseek/deepseek-chat"

# Carregar variáveis de ambiente
load_dotenv()

@dataclass
class FerramentaProducao:
    """Estrutura para ferramentas de produção (Partes 1, 2, 3)."""
    id_item_completo: str  # ID completo com bonus IDs se houver
    nome_ptbr: str
    profissao: str
    qualidade: str  # "Rara" ou "Épica"
    item_level: int
    rank: int = 5
    atributo_tipo: str = ""
    atributo_valor: int = 0
    bonus_ids: List[str] = None
    url: str = ""

    def __post_init__(self):
        if self.bonus_ids is None:
            self.bonus_ids = []

@dataclass
class EncantamentoFerramenta:
    """Estrutura para encantamentos de ferramenta (Parte 4)."""
    id: str
    nome_ptbr: str
    rank: int = 2
    atributo_tipo: str = ""
    atributo_valor: int = 0
    url: str = ""

@dataclass
class MissivaProfissao:
    """Estrutura para missivas talassianas (Parte 5)."""
    id: str
    nome_ptbr: str
    atributo_vinculado: str = ""
    valor_atributo: str = ""
    url: str = ""

class WowheadScraperCompleto:
    """Scraper completo para todas as 5 partes do WoWhead Midnight."""

    def __init__(self):
        self.base_url = os.getenv("WOWHEAD_BASE_URL", "https://www.wowhead.com")
        self.quality_rank = int(os.getenv("QUALITY_RANK", 5))
        # Season 2: faixa de ilvl configurável (padrão 305-350)
        self.ilvl_min = int(os.getenv("ILVL_MIN", ILVL_PISO_PADRAO))
        self.ilvl_max = int(os.getenv("ILVL_MAX", ILVL_TETO_PADRAO))
        self.rare_item_level = int(os.getenv("RARE_ITEM_LEVEL", self.ilvl_min))
        self.epic_item_level_min = int(os.getenv("EPIC_ITEM_LEVEL_MIN", self.ilvl_min))

        # Configurar o crawler
        self.browser_config = BrowserConfig(
            headless=os.getenv("CRAWL4AI_BROWSER_HEADLESS", "true").lower() == "true",
            enable_stealth=os.getenv("CRAWL4AI_MAGIC_MODE", "true").lower() == "true",
            verbose=False,
            browser_type="chromium",
            viewport_width=1920,
            viewport_height=1080
        )

        # Configurar estratégia de extração com LLM
        self.llm_config = LLMConfig(
            provider=LLM_PROVIDER,
            api_token=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.1,
            max_tokens=2000
        )

        self.crawler = AsyncWebCrawler(config=self.browser_config)

    async def __aenter__(self):
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    def extract_item_id_from_url(self, url: str) -> str:
        """Extrai o ID do item da URL do WoWhead."""
        match = re.search(r'item=(\d+)', url)
        if match:
            return match.group(1)
        return ""

    def extract_bonus_ids_from_url(self, url: str) -> List[str]:
        """Extrai todos os bonus IDs da URL."""
        bonus_ids = []

        # Extrair parâmetros do caminho (WoWhead usa formato /item=12345&bonus=... no caminho)
        match = re.search(r'item=\d+(.*?)(?:#|$)', url)
        if match:
            params_str = match.group(1)
            # Extrair parâmetros como &bonus=... &gems=... &ench=...
            param_pattern = r'&(bonus|gems|ench)=([^&]+)'
            for param_match in re.finditer(param_pattern, params_str):
                param_value = param_match.group(2)

                # Separar valores por : ou ,
                for id_val in re.split(r'[:,]', param_value):
                    if id_val and id_val.isdigit():
                        bonus_ids.append(id_val)

        return bonus_ids

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
            if key in url:
                return value

        return "Desconhecida"

    async def extrair_ferramentas_parte(self, urls: List[str], parte_num: int) -> List[FerramentaProducao]:
        """Extrai ferramentas de produção para uma parte específica."""
        items = []

        for url in urls:
            print(f"[Parte {parte_num}] Processando: {url}")

            profissao = self.get_profession_from_url(url)

            # Prompt específico conforme as especificações
            prompt = f"""Acesse o guia de profissão de Midnight fornecido.
Localize a seção 'Accessories & Tools'.
Filtre apenas itens de qualidade Rara (Azul) e Épica (Roxa).
Entre em cada link individual e ajuste o seletor para o Rank 5.
Verifique o Item Level na faixa da Season 2 (Herói 305-321, Herói Voidforge 328, Mito 318-334, Mito Voidforge 341, Very Rare até 344).
Se o item permitir variação de atributos via missiva, capture o ID completo (incluindo Bonus IDs) para cada uma das 5 ou mais variações possíveis.
Gere uma entrada separada no JSON para cada variação de atributo.

Para cada item, capture:
1. ID completo do item (com bonus IDs se houver)
2. Nome em PT-BR
3. Profissão: {profissao}
4. Qualidade (Rara/Épica)
5. Item Level
6. Rank (sempre 5)
7. Tipo de atributo (ex: Engenhosidade, Finesse, etc.)
8. Valor do atributo (número inteiro)

Retorne como uma lista de objetos JSON com os campos especificados."""

            try:
                result = await self.crawler.arun(
                    url=url,
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config=self.llm_config,
                        instruction=prompt,
                        schema=FERRAMENTAS_PRODUCAO_SCHEMA
                    )
                )

                if result.success and result.extracted_content:
                    try:
                        data = json.loads(result.extracted_content)
                        if isinstance(data, dict) and "ferramentas_producao" in data:
                            items_data = data["ferramentas_producao"]
                        elif isinstance(data, list):
                            items_data = data
                        else:
                            items_data = []

                        for item_data in items_data:
                            # Extrair bonus IDs da URL se disponível
                            item_url = item_data.get("url", url)
                            bonus_ids = self.extract_bonus_ids_from_url(item_url)

                            # Construir ID completo
                            base_id = self.extract_item_id_from_url(item_url)
                            if bonus_ids:
                                id_completo = f"{base_id}&bonus={':'.join(bonus_ids)}"
                            else:
                                id_completo = base_id

                            item = FerramentaProducao(
                                id_item_completo=id_completo,
                                nome_ptbr=item_data.get("nome_ptbr", ""),
                                profissao=item_data.get("profissao", profissao),
                                qualidade=item_data.get("qualidade", ""),
                                item_level=item_data.get("item_level", 0),
                                rank=item_data.get("rank", 5),
                                atributo_tipo=item_data.get("atributo_tipo", ""),
                                atributo_valor=item_data.get("atributo_valor", 0),
                                bonus_ids=bonus_ids,
                                url=item_url
                            )

                            # Aplicar filtros de qualidade
                            if self._passa_filtros_qualidade(item):
                                items.append(item)
                            else:
                                print(f"  Item filtrado: {item.nome_ptbr} (ILvl: {item.item_level}, Qualidade: {item.qualidade})")

                    except json.JSONDecodeError as e:
                        print(f"  Erro ao decodificar JSON: {e}")
                        print(f"  Conteúdo: {result.extracted_content[:500]}...")

            except Exception as e:
                print(f"  Erro ao processar URL: {e}")

        return items

    async def extrair_encantamentos(self) -> List[EncantamentoFerramenta]:
        """Extrai encantamentos de ferramenta (Parte 4)."""
        items = []

        for url in PARTE4_URLS:
            print(f"[Parte 4] Processando encantamento: {url}")

            item_id = self.extract_item_id_from_url(url)

            prompt = f"""Para o encantamento no link fornecido, capture:
1. ID oficial: {item_id}
2. Nome do encantamento em PT-BR
3. Rank (selecione o Rank 2 - Máximo)
4. Tipo de atributo concedido (ex: Engenhosidade, Finesse, etc.)
5. Valor numérico do bônus para a expansão Midnight

Retorne como um objeto JSON com os campos especificados."""

            try:
                result = await self.crawler.arun(
                    url=url,
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config=self.llm_config,
                        instruction=prompt,
                        schema=ENCANTAMENTOS_FERRAMENTA_SCHEMA
                    )
                )

                if result.success and result.extracted_content:
                    try:
                        data = json.loads(result.extracted_content)
                        if isinstance(data, dict) and "encantamentos_ferramenta" in data:
                            items_data = data["encantamentos_ferramenta"]
                        elif isinstance(data, list):
                            items_data = data
                        else:
                            items_data = [data]

                        for item_data in items_data:
                            item = EncantamentoFerramenta(
                                id=item_data.get("id", item_id),
                                nome_ptbr=item_data.get("nome_ptbr", ""),
                                rank=item_data.get("rank", 2),
                                atributo_tipo=item_data.get("atributo_tipo", ""),
                                atributo_valor=item_data.get("atributo_valor", 0),
                                url=url
                            )
                            items.append(item)

                    except json.JSONDecodeError as e:
                        print(f"  Erro ao decodificar JSON: {e}")

            except Exception as e:
                print(f"  Erro ao processar URL: {e}")

        return items

    async def extrair_missivas(self) -> List[MissivaProfissao]:
        """Extrai missivas talassianas (Parte 5)."""
        items = []

        for url in PARTE5_URLS:
            print(f"[Parte 5] Processando missiva: {url}")

            item_id = self.extract_item_id_from_url(url)

            prompt = f"""Para a missiva talassiana no link fornecido, capture:
1. ID: {item_id}
2. Nome oficial em Português
3. Atributo de profissão que esta missiva define (ex: Engenhosidade, Finesse, etc.)
4. Valores de status que ela agrega aos equipamentos

Retorne como um objeto JSON com os campos especificados."""

            try:
                result = await self.crawler.arun(
                    url=url,
                    extraction_strategy=LLMExtractionStrategy(
                        llm_config=self.llm_config,
                        instruction=prompt,
                        schema=MISSIVAS_PROFISSOES_SCHEMA
                    )
                )

                if result.success and result.extracted_content:
                    try:
                        data = json.loads(result.extracted_content)
                        if isinstance(data, dict) and "missivas_profissoes" in data:
                            items_data = data["missivas_profissoes"]
                        elif isinstance(data, list):
                            items_data = data
                        else:
                            items_data = [data]

                        for item_data in items_data:
                            item = MissivaProfissao(
                                id=item_data.get("id", item_id),
                                nome_ptbr=item_data.get("nome_ptbr", ""),
                                atributo_vinculado=item_data.get("atributo_vinculado", ""),
                                valor_atributo=item_data.get("valor_atributo", ""),
                                url=url
                            )
                            items.append(item)

                    except json.JSONDecodeError as e:
                        print(f"  Erro ao decodificar JSON: {e}")

            except Exception as e:
                print(f"  Erro ao processar URL: {e}")

        return items

    def _passa_filtros_qualidade(self, item: FerramentaProducao) -> bool:
        """Aplica filtros de qualidade/ilvl da Season 2 (305-350 por padrão)."""
        # Verificar qualidade
        if item.qualidade.lower() not in ["rara", "épica", "epica"]:
            return False

        # Verificar rank
        if item.rank != 5:
            return False

        # Verificar faixa de item level (sem travas antigas de 232/250)
        ilvl = int(item.item_level or 0)
        if ilvl and (ilvl < self.ilvl_min or ilvl > self.ilvl_max):
            return False

        return True

    async def executar_scraping_completo(self):
        """Executa o scraping completo de todas as 5 partes."""
        print("=== Iniciando Scraping Completo WoWhead Midnight ===")
        print()

        todos_itens = {
            "parte1_ferramentas": [],
            "parte2_ferramentas": [],
            "parte3_ferramentas": [],
            "parte4_encantamentos": [],
            "parte5_missivas": []
        }

        # Parte 1: Ferramentas de Produção (Grupo 1)
        print("=== PARTE 1: Ferramentas de Produção (Alquimia, Ferraria, Culinária, Encantamento, Engenharia) ===")
        items_parte1 = await self.extrair_ferramentas_parte(PARTE1_URLS, 1)
        todos_itens["parte1_ferramentas"] = [asdict(item) for item in items_parte1]
        print(f"Extraídos {len(items_parte1)} itens da Parte 1")
        print()

        # Parte 2: Ferramentas de Coleta e Joalheria (Grupo 2)
        print("=== PARTE 2: Ferramentas de Coleta e Joalheria (Pesca, Herborismo, Escrivania, Joalheria, Couraria) ===")
        items_parte2 = await self.extrair_ferramentas_parte(PARTE2_URLS, 2)
        todos_itens["parte2_ferramentas"] = [asdict(item) for item in items_parte2]
        print(f"Extraídos {len(items_parte2)} itens da Parte 2")
        print()

        # Parte 3: Restante das Profissões (Grupo 3)
        print("=== PARTE 3: Restante das Profissões (Mineração, Esfolamento, Alfaiataria) ===")
        items_parte3 = await self.extrair_ferramentas_parte(PARTE3_URLS, 3)
        todos_itens["parte3_ferramentas"] = [asdict(item) for item in items_parte3]
        print(f"Extraídos {len(items_parte3)} itens da Parte 3")
        print()

        # Parte 4: Encantamentos de Ferramenta
        print("=== PARTE 4: Encantamentos de Ferramenta ===")
        items_parte4 = await self.extrair_encantamentos()
        todos_itens["parte4_encantamentos"] = [asdict(item) for item in items_parte4]
        print(f"Extraídos {len(items_parte4)} encantamentos")
        print()

        # Parte 5: Missivas Talassianas
        print("=== PARTE 5: Missivas Talassianas ===")
        items_parte5 = await self.extrair_missivas()
        todos_itens["parte5_missivas"] = [asdict(item) for item in items_parte5]
        print(f"Extraídos {len(items_parte5)} missivas")
        print()

        # Salvar resultados
        await self.salvar_resultados_completos(todos_itens)
        return todos_itens

    async def salvar_resultados_completos(self, resultados: Dict[str, Any]):
        """Salva os resultados completos em arquivos JSON."""
        # Criar diretório data se não existir
        os.makedirs("data", exist_ok=True)

        # Salvar resultados completos
        with open("data/wowhead_all_items.json", "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=2)
        print("Resultados completos salvos em data/wowhead_all_items.json")

        # Salvar resultados por parte
        for parte_nome, itens in resultados.items():
            if itens:  # Só salvar se houver itens
                filename = f"data/wowhead_{parte_nome}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(itens, f, ensure_ascii=False, indent=2)
                print(f"  - {parte_nome}: {len(itens)} itens salvos em {filename}")

        # Gerar resumo estatístico
        total_itens = sum(len(itens) for itens in resultados.values())
        print(f"\n=== RESUMO FINAL ===")
        print(f"Total de itens extraídos: {total_itens}")
        for parte_nome, itens in resultados.items():
            print(f"  {parte_nome}: {len(itens)} itens")

async def main():
    """Função principal para executar o scraper completo."""
    print("=== Scraper WoWhead Midnight - Execução Completa ===")
    print("Este processo pode levar vários minutos devido à extração com LLM.")
    print()

    async with WowheadScraperCompleto() as scraper:
        try:
            resultados = await scraper.executar_scraping_completo()
            print("\n=== Scraping concluído com sucesso! ===")
            return resultados
        except Exception as e:
            print(f"\n=== Erro durante o scraping: {e} ===")
            import traceback
            traceback.print_exc()
            return None

if __name__ == "__main__":
    asyncio.run(main())


