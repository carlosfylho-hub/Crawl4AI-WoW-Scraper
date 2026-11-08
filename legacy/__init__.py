"""Testes legados mantidos apenas como referência histórica.

`test_final.py` era o antigo "teste final" do projeto: instanciava a classe do
scraper e fazia uma requisição à httpbin.org. Ele passava mesmo com o pipeline
de extração 100% quebrado, por isso foi aposentado em favor de:

- [`tests/test_contrato_crawl4ai.py`](../tests/test_contrato_crawl4ai.py:1)
- [`tests/test_smoke_offline.py`](../tests/test_smoke_offline.py:1)
"""
