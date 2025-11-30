import os
from concurrent import futures

import grpc
import joblib
import numpy as np

import model_pb2
import model_pb2_grpc


MODEL_PATH = os.getenv("MODEL_PATH", "models/catboost_model_test_109.pkl")
MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
PORT = int(os.getenv("PORT", "50051"))


class PredictionService(model_pb2_grpc.PredictionServiceServicer):
    def __init__(self) -> None:
        print(f"[server] Loading model from: {MODEL_PATH}")
        self.model = joblib.load(MODEL_PATH)
        self.model_version = MODEL_VERSION
        print("[server] Model loaded")

    def Health(self, request, context):
        return model_pb2.HealthResponse(
            status="ok",
            model_version=self.model_version,
        )

    def Predict(self, request, context):

        import time

        sleep_ms = int(os.getenv("SLEEP_MS", "0"))
        if sleep_ms > 0:
            time.sleep(sleep_ms / 1000.0)

        try:
            if not request.features:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("features must be non-empty")
                return model_pb2.PredictResponse()

            x = np.array(request.features, dtype=float).reshape(1, -1)


            y_pred = self.model.predict(x)
            if isinstance(y_pred, (list, tuple, np.ndarray)):
                y_value = float(y_pred[0])
            else:
                y_value = float(y_pred)


            confidence = 1.0
            if hasattr(self.model, "predict_proba"):
                try:
                    proba = self.model.predict_proba(x)
                    confidence = float(np.max(proba))
                except Exception:
                    confidence = 1.0

            return model_pb2.PredictResponse(
                prediction=str(y_value),
                confidence=confidence,
                model_version=self.model_version,
            )

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Prediction failed: {e}")
            return model_pb2.PredictResponse()


def serve() -> None:
    options = [
        ("grpc.max_send_message_length", 50 * 1024 * 1024),
        ("grpc.max_receive_message_length", 50 * 1024 * 1024),
    ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=4),
        options=options,
    )
    model_pb2_grpc.add_PredictionServiceServicer_to_server(
        PredictionService(),
        server,
    )
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"[server] gRPC server started on port {PORT}")
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except Exception:
        pass

    serve()
