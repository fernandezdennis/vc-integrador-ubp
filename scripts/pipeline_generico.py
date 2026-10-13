import cv2
import pandas as pd
from ultralytics import YOLO
from utils_color import is_red_vehicle
from camara_rois import CAMERA_CONFIG
CLASSES_INTERES = ["person", "car", "motorcycle", "bicycle", "truck"]

model = YOLO("yolov8n.pt")   # o tu modelo fine-tuneado


def inside_exclusion_zone(camera_id, xc, yc):

    zones = CAMERA_CONFIG[camera_id]["exclusion_zones"]

    for z in zones:
        if (
            z["x1"] <= xc <= z["x2"]
            and
            z["y1"] <= yc <= z["y2"]
        ):
            print(
                "ROI HIT",
                camera_id,
                z["name"],
                xc,
                yc
            )
            return True
        if (
            z["x1"] <= xc <= z["x2"] and
            z["y1"] <= yc <= z["y2"]
        ):
            return True

    return False

def get_timestamp(frame_idx, fps):
    return frame_idx / fps


def procesar_video(video_path, camera_id, csv_output_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_idx = 0
    print("PIPELINE GENERICO VERSION NUEVA")
    print("video_path =", video_path)
    print("camera_id =", camera_id)
    print("CONFIG CAMARA")
    print(CAMERA_CONFIG[camera_id])
    eventos = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        h, w, _ = frame.shape
        timestamp_s = get_timestamp(frame_idx, fps)

        results = model(frame)[0]
        local_id = 0

        for box in results.boxes:
            cls_idx = int(box.cls[0])
            clase_nombre = model.names[cls_idx]

            if clase_nombre not in CLASSES_INTERES:
                continue

            xc, yc, bw, bh = box.xywhn[0].tolist()
            if inside_exclusion_zone(camera_id, xc, yc):
                print(
                    f"EXCLUIDO -> {camera_id} "
                    f"{clase_nombre} "
                    f"({xc:.3f},{yc:.3f})"
                )
                continue

            x_center = int(xc * w)
            y_center = int(yc * h)
            box_w = int(bw * w)
            box_h = int(bh * h)

            x1 = max(0, x_center - box_w // 2)
            y1 = max(0, y_center - box_h // 2)
            x2 = min(w, x_center + box_w // 2)
            y2 = min(h, y_center + box_h // 2)

            roi = frame[y1:y2, x1:x2]

            is_red = False
            if clase_nombre in ["car", "motorcycle", "bicycle", "truck"]:
                is_red = is_red_vehicle(roi,
                                        ratio_threshold=0.12,
                                        spread_threshold=0.25)

            local_id += 1

            eventos.append([
                timestamp_s, frame_idx, camera_id,
                local_id, clase_nombre, is_red,
                xc, yc, bw, bh
            ])

        frame_idx += 1

    cap.release()

    df = pd.DataFrame(eventos, columns=[
        "timestamp_s", "frame", "camera",
        "local_id", "class", "is_red",
        "xc", "yc", "bw", "bh"
    ])

    df.to_csv(csv_output_path, index=False)
    print(f"✔ CSV generado: {csv_output_path}")
