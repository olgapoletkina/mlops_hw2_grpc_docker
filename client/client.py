import grpc

import model_pb2
import model_pb2_grpc


def main():
    channel = grpc.insecure_channel("localhost:50051")
    stub = model_pb2_grpc.PredictionServiceStub(channel)

    health_resp = stub.Health(model_pb2.HealthRequest(), timeout=2.0)
    print(f"Health: status={health_resp.status}, version={health_resp.model_version}")

    features_example = [
        4.2,  # wall_length
        0.0,  # room_1_start_fraction
        0.6,  # room_1_end_fraction
        0.6,  # room_1_wall_fraction
        0.6,  # room_2_start_fraction
        1.0,  # room_2_end_fraction
        0.4,  # room_2_wall_fraction
    ]

    predict_req = model_pb2.PredictRequest(features=features_example)
    predict_resp = stub.Predict(predict_req, timeout=5.0)

    print(
        f"Predict: prediction={predict_resp.prediction}, "
        f"confidence={predict_resp.confidence:.4f}, "
        f"version={predict_resp.model_version}"
    )


if __name__ == "__main__":
    main()
