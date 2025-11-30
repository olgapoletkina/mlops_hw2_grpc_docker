## **Описание**

Этот проект реализует полноценный **gRPC-сервис для ML-модели**, обученной в ДЗ №1 (CatBoost).
Сервис предоставляет два метода:

* **Health** — проверка статуса сервиса.
* **Predict** — получение предсказания модели на основе входного вектора признаков.

Сервис полностью контейнеризирован, запускается как локально, так и внутри Docker.

---

## **Структура**

```
ml_grpc_service/
│
├── client/
│   └── client.py          # gRPC-клиент
│
├── server/
│   └── server.py          # gRPC-сервер
│
├── models/
│   └── catboost_model_test_109.pkl   # модель из ДЗ №1
│
├── protos/
│   └── model.proto        # protobuf контракт
│
├── model_pb2.py
├── model_pb2_grpc.py
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
└── README.md
```

---

## **Функциональность**

### Health Check

Метод:

```
mlservice.v1.PredictionService.Health
```

Возвращает:

* статус `"ok"`
* версию загруженной модели

### Predict

Метод:

```
mlservice.v1.PredictionService.Predict
```

Принимает:

* `repeated double features` — список входных признаков (как в HW1)

Возвращает:

* строковое предсказание
* confidence
* version модели

---

## **Protobuf контракт**

Файл: `protos/model.proto`

```proto
syntax = "proto3";

package mlservice.v1;

service PredictionService {
  rpc Health(HealthRequest) returns (HealthResponse);
  rpc Predict(PredictRequest) returns (PredictResponse);
}

message HealthRequest {}

message HealthResponse {
  string status = 1;
  string model_version = 2;
}

message PredictRequest {
  repeated double features = 1;
}

message PredictResponse {
  string prediction = 1;
  double confidence = 2;
  string model_version = 3;
}
```

---

## **Запуск локально**

### Активировать виртуальное окружение

```bash
python -m venv mlops_hw2_venv
mlops_hw2_venv\Scripts\activate
```

### Установить зависимости

```bash
pip install -r requirements.txt
```

### Запустить сервер

```bash
python -m server.server
```

Ожидаемый вывод:

```
[server] Loading model from: models/catboost_model_test_109.pkl
[server] Model loaded
[server] gRPC server started on port 50051
```

### Запустить клиента

```bash
python -m client.client
```

Ожидаемый вывод:

```
Health: status=ok, version=v1.0.0
Predict: prediction=1.0, confidence=0.87, version=v1.0.0
```

---

## **Запуск в Docker**

### Перейти в директорию:

```bash
cd ml_grpc_service
```

### Собрать образ:

```bash
docker build -t grpc-ml-service .
```

### Запустить контейнер:

```bash
docker run -p 50051:50051 grpc-ml-service
```

---

## **Проверка /health через grpcurl**

Установить grpcurl:
[https://github.com/fullstorydev/grpcurl](https://github.com/fullstorydev/grpcurl)

И выполнить:

```bash
grpcurl -plaintext localhost:50051 mlservice.v1.PredictionService.Health
```

Ожидаемый ответ:

```json
{
  "status": "ok",
  "modelVersion": "v1.0.0"
}
```

---

## **Проверка /predict через grpcurl**

```bash
grpcurl -plaintext \
  -d '{"features":[-1.33,1.02,0.44,-0.81,-1.01,0.52,-0.21,1.61]}' \
  localhost:50051 \
  mlservice.v1.PredictionService.Predict
```

---

## **Переменные окружения**

| Название        | По умолчанию                              | Назначение                        |
| --------------- | ----------------------------------------- | --------------------------------- |
| `PORT`          | `50051`                                   | порт сервера                      |
| `MODEL_PATH`    | `/app/models/catboost_model_test_109.pkl` | путь к модели внутри контейнера   |
| `MODEL_VERSION` | `v1.0.0`                                  | версия модели                     |
| `SLEEP_MS`      | `0`                                       | искусственная задержка для тестов |

---

## **Итоги проекта**

В рамках проекта реализовано:

    - gRPC-API для ML-модели
    - Protobuf контракт
    - Сервер и клиент
    - Поддержка версионирования модели
    - Корректная обработка ошибок
    - Контейнеризация сервиса
    - Локальный тест сервер + клиент

