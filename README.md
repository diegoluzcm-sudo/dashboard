# Dashboard Comercial

Dashboard comercial em Streamlit com tema escuro, indicadores financeiros, funil de vendas, rankings de SDRs e Closers, filtros temporais, metas e integração com planilhas Google Sheets.

## Execução local

```bash
pip install -r requirements.txt
streamlit run main.py
```

## Publicação

No Streamlit Community Cloud, selecione este repositório, a branch `main` e o arquivo `main.py` como arquivo principal.

As planilhas precisam estar compartilhadas com permissão de visualização para qualquer pessoa com o link, ou ser substituídas por upload de CSV/XLSX dentro do aplicativo.

## Fontes configuradas

- Planilha permanente de vendas, com abas mensais.
- Planilha do ciclo de vendas.
- Planilha de realizadas dos SDRs e informações de Closers.

O aplicativo padroniza `Santana` e `Sant’Anna` como o mesmo Closer.

## Dependências

As dependências estão em `requirements.txt`.
