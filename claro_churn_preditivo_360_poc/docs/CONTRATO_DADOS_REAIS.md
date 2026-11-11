# Gate para uso futuro de dados reais — ainda não iniciado

A POC é autônoma e sintética. Antes de qualquer aplicação à Claro:

1. Confirmar unidade de observação (CPF pseudonimizado, contrato, linha ou família de produtos) e definição de churn total/parcial.
2. Mapear chaves, cardinalidades e datas de vigência nas tabelas Oracle autorizadas.
3. Definir população elegível, formas de exclusão, cortes e medidas de qualidade.
4. Definir as colunas de faturamento, pagamento, inadimplência e estornos, com semântica de liquidação e vencimento.
5. Incluir URA, CRM, lojas/PDV, app/site, visitas técnicas, consumo e dados de rede somente se existir cobertura histórica suficiente.
6. Registrar proveniência, fonte, data de publicação, licença e granularidade regional de cada indicador externo.
7. Obter avaliação de segurança, governança, minimização/pseudonimização e LGPD com os responsáveis.
8. Recriar treino e teste temporais com várias safras reais, controlar drift e avaliar por segmento.
9. Revisar contra-factualidade, vieses, equidade e impacto das ações sugeridas.
10. Definir capacidade de atendimento, thresholds com negócio e revisão humana.
11. Construir adaptadores específicos após aprovar o dicionário real; **não substituir CSVs por arquivos não homologados**.

Não há conexão, query, credenciais nem coleta Oracle no código entregue.
