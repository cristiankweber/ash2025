# 🩸 ASH-SAP Study Platform (Modo Offline)

Plataforma de estudo em Hematologia que importa e organiza suas lições do Claude.

**100% OFFLINE - NÃO precisa de API key!**

## Como Funciona

1. Você estuda com o Claude (claude.ai)
2. Copia o JSON das lições geradas
3. Importa no app
4. Revisa, acompanha progresso e organiza seu estudo

## Instalação

```bash
cd ash_study
pip install -r requirements.txt
streamlit run app.py
```

Pronto! Não precisa configurar nada.

## Funcionalidades

- **📥 Importar Lições** - Cole o JSON das suas conversas
- **📚 9 Trilhas** - Organizadas por tema do ASH-SAP
- **📖 Ver Lições** - Revise objetivos, tópicos e pontos-chave
- **📊 Progresso** - Acompanhe seu avanço
- **📤 Exportar** - Faça backup do seu progresso

## Formato do JSON

O app aceita o JSON no formato que o Claude gera:

```json
{
  "licoes_concluidas": [
    {
      "capitulo_ash_sap": 1,
      "titulo": "Manejo Perioperatório",
      "objetivos_aprendizado": ["..."],
      "topicos_abordados": [...],
      "pontos_chave_memorizacao": ["..."],
      "avaliacao": {
        "total_questoes": 7,
        "questoes_corretas": 5,
        "taxa_acerto": 71.4
      }
    }
  ]
}
```

## Trilhas Disponíveis

1. Hemostasia e Trombose (Cap. 15-22)
2. Anemias (Cap. 6-9, 12-14, 35, 39)
3. Hemoglobinopatias (Cap. 10-11)
4. Plaquetas (Cap. 23-26)
5. Neoplasias Mieloides (Cap. 34, 36-41)
6. Neoplasias Linfoides (Cap. 42-49)
7. Transplante (Cap. 30-33)
8. Medicina Transfusional (Cap. 27-29)
9. Hematologia Consultiva (Cap. 1-5)

## Dica de Uso

Quando estudar no Claude, peça para ele gerar as lições neste formato JSON.
Assim você pode importar facilmente no app!
