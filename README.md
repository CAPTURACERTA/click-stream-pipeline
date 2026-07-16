# Click Stream Pipeline

Projeto de estudo e portfólio que simula um pipeline de eventos de um e-commerce. Ele gera usuários, produtos e clicks, trafega essas mensagens por um broker assíncrono em memória, valida os dados e persiste informações em MongoDB e Redis.

O objetivo não é substituir Kafka, RabbitMQ ou uma plataforma de streaming gerenciada. É tornar visíveis, em uma base pequena e legível, os conceitos que aparecem em sistemas orientados a eventos de engenharia de dados.

## O que este projeto demonstra

- Modelagem e serialização de eventos com `dataclasses`, JSON, `ObjectId` e timestamps UTC.
- Separação entre eventos brutos e eventos validados.
- Padrão pub/sub com consumidores independentes e assíncronos.
- Persistência documental no MongoDB, preservando tipos BSON nativos.
- Métricas de clicks no Redis: contadores por produto/usuário e ranking por visualizações.
- Tratamento de eventos inválidos, logging e propagação de falhas de consumidores.
- Latência de rede simulada de forma não bloqueante nas operações assíncronas de infraestrutura.
- Testes automatizados sem exigir MongoDB ou Redis em execução.

## Arquitetura

```text
Generator
   │
   ├── users:raw ─────► UserValidationConsumer ─────► users:validated ─────► MongoDB/users
   ├── products:raw ──► ProductValidationConsumer ─► products:validated ──► MongoDB/products
   └── clicks:raw ────► ClickValidationConsumer ───► clicks:validated ────┬► MongoDB/clicks
                                                                            └► Redis metrics/ranking
```

O `MessageBroker` é deliberadamente em memória e serve ao aprendizado: ele cria uma fila por tópico, aguarda o término do processamento com `drain()` e encerra tarefas de despacho de forma limpa. Em um ambiente de produção, essa peça seria substituída por um broker durável, como Kafka ou RabbitMQ.

## Fluxo dos dados

1. O gerador cria usuários, produtos e clicks. Uma pequena parcela dos eventos é propositalmente inválida.
2. Os eventos chegam aos tópicos `*:raw`.
3. Consumidores de validação descartam e registram eventos inválidos; os demais seguem para `*:validated`.
4. Consumidores MongoDB armazenam usuários, produtos e clicks válidos.
5. O consumidor Redis atualiza, em uma transação, views por produto, clicks por usuário e o ranking de produtos.

## Tecnologias

- Python 3.12+
- `asyncio`
- MongoDB / PyMongo Async
- Redis / redis-py Async
- Faker
- Pytest

## Como executar

Instale as dependências:

```bash
uv sync
```

Suba MongoDB e Redis localmente. Com Docker, por exemplo:

```bash
docker run --rm -d --name click-stream-mongo -p 27017:27017 mongo
docker run --rm -d --name click-stream-redis -p 6379:6379 redis
```

Execute o pipeline:

```bash
uv run python main.py
```

Os logs são exibidos no terminal e gravados em `pipeline.log`.

## Consultando os resultados

MongoDB:

```bash
mongosh
use e-commerce
db.users.find()
db.products.find()
db.clicks.find()
```

Redis:

```bash
redis-cli ZREVRANGE products:rank:views 0 -1 WITHSCORES
redis-cli HGETALL products:<product_id>
redis-cli HGETALL users:<user_id>
```

## Testes

O projeto usa `pytest` como ferramenta de testes. A suíte é unitária e não exige MongoDB ou Redis em execução; os serviços externos ficam reservados para futuros testes de integração.

Ela cobre:

- serialização e restauração dos eventos, preservando valores compatíveis com BSON;
- validação de modelos e descarte de eventos inválidos;
- entrega de mensagens e propagação de erros no broker;
- comportamento assíncrono do simulador de latência.

Instale também as dependências de desenvolvimento e execute:

```bash
uv sync --group dev
uv run pytest
```

Para uma saída mais detalhada:

```bash
uv run pytest -v
```

## Nota de portfólio

Este repositório foi construído como exercício prático para estudar os fundamentos de pipelines guiados a eventos. As escolhas privilegiam clareza e rastreabilidade do fluxo, deixando explícitos os limites entre a simulação didática e as preocupações de um sistema distribuído de produção.
