
### runserver 
Services are divided in multiple django projects (single-app) : ledger_service, transaction_service, wallet-service(yes, -)
Each project has similar dockerfile check at `ledger_service/Dockerfile` 

see `docker-compose.yml` file, `transaction_service:`
We run management commands in seprate containers(same project). Means docker compose will build same project again (build ./ledger_service) only to run `ONE` management command like : python manage.py consume_ledger_events

***command in docker-compose.yml overrides CMD in the Dockerfile.*** So,
CMD ["gunicorn", "wallet-service.wsgi:application", "--bind", "0.0.0.0:8000"] (this command is in Dockerfile) will not run for `transaction_consumer` since we have a command for this serivce in docekr-compose(see the `docker-compose.yml` file).

Notice ports are not mentioned in outbox events and consumers since they won't be serving anything.

### communication 
Since containers are seprate OS(different ip), we specify in docker-compose, something like 
ports:
    - "8000:8000"
Host → container port mapping (Left side = host port, right side = container port)

"8001:8000", in wallet-service's ports section means 
***make wallet-service's port 8000 accesible to host from host's port 8001, hence http://localhost:8001/ hits the django server(port:8000) runing on wallet-service container***

similarly we have 8000:8000 in transaction service means 
from host we can access transaction service's django server from host like : `localhost:8000` 

We add "ports" section only when we want outside connection,
***All services in the same docker-compose.yml are automatically put on the same private Docker network.***
If we don't add ports section, services will still be able communicate with each other.
Hence transaction_service communicates with wallet-service by internal DNS like : http://wallet-service:8000 

Similarly for kafka and db, see `environment:` in transaction service section in docker-compose file, 
```
environment : 
    DATABASE_URL: postgres://postgres:postgres@transaction_db:5432/transaction_db
    KAFKA_BOOTSTRAP_SERVERS: kafka:9092
here, 
    db : transaction_db:5432 (in DATABASE_URL)
    kafka : kafka:9092
```
docker-compose DNS resolves kafka (service name) -> internal ip of kafka container

### debug 
kafka-console-consumer --bootstrap-server kafka:9092 --topic wallet.events --from-beginning

POST : http://localhost:8000/transfer 
```
{
    "sender_wallet_id": "11111111-1111-1111-1111-111111111111",
    "receiver_wallet_id": "22222222-2222-2222-2222-222222222222",
    "amount": "3.00",
    "idempotency_key": "tx-1"
}
``` 


### overview

***In microservices each service may or may not be on same server but should be independently deployable***
***Service 1 can use the http or gRPC protocol to communicate with Service 2 without any broker, but it will not be asynchronous since Service 1 will have to wait for other Service 2 to execute and return a response.***
***Django best practice: background processes = management commands***
***In microservices consumer runs in background not tied to generic http requests***

```
Transaction Service = coordinator, not owner of money (entry point)
Ledger = source of truth
Wallet = cached snapshot
``` 
- The entry-point transaction service calls wallet service synchronously because we need to inform user immediately if sender wallet sufficient money.
- if sufficient money is there, then atomically : amount is reserved, outbox event is created and status 200 is sent, else 400 is sent, this ends the synchronous part
- creation of wallet reserve outboxing event starts the chain of asynchronously flow

### /transfer API

initiate_transfer() 

`transaction_service\transactions\views.py`

reserve_funds()

`wallet-service\wallets\views.py`

outbox events are checked in every 1s gap. If found "WALLET_RESERVED" topic is published to kafka "wallet.events"

`wallet-service\wallets\management\commands\publish_outbox.py`

ledger consumes "WALLET_RESERVED". Atomically updates ledger and creates outbox events (to publish success)

`ledger_service\ledger\management\commands\consume_wallet_events.py`
`ledger_service\ledger\management\commands\publish_outbox.py`

wallet and transaction service consumes "ledger.events" topics "LEDGER_SUCCESS" and "LEDGER_FAILURE"

`wallet-service\wallets\management\commands\consume_ledger_events.py`
`transaction_service\transactions\management\commands\consume_ledger_events.py`

https://chatgpt.com/g/g-p-6966321e55f0819190b8c9607359e430-digital-wallet/c/696b5910-0cec-8325-af06-bddca8794c37

##### reconcilation :
is verifying correctness by comparing wallet service with sum of amount ledger instances, it never modifies the ledger instances in case of mismatch, but creates new ledger entry. 

##### features to add : 
User authentication and registration 
Transaction history with timestamp & status 
Credit and debit to wallet 
Wallet to wallet transfer 
View balance 
See a transaction details/status
 
