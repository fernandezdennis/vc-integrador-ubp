import cv2
import os

from networkx import display
from camara_rois import CAMERA_CONFIG
# ============================
# CONFIGURACIÓN
# ============================

IMAGES_DIR = "dataset/images"
LABELS_DIR = "dataset/labels"

CLASSES = ["person", "car", "motorcycle", "bicycle", "truck"]

HANDLE_SIZE = 2     # tamaño de las esquinas
ZOOM_STEP = 0.1      # incremento de zoom
MAX_ZOOM = 3.0
MIN_ZOOM = 0.5

# ============================
# VARIABLES GLOBALES
# ============================

current_boxes = []
selected_box = None
selected_handle = None
dragging = False
zoom = 1.0


# ============================
# FUNCIONES DE ETIQUETAS
# ============================

def load_labels(label_path):
    boxes = []
    if os.path.exists(label_path):
        with open(label_path, "r") as f:
            for line_number, line in enumerate(f, start=1):
                values = line.split()
                if not values:
                    continue
                if len(values) != 5:
                    print(f"Línea ignorada en {label_path}:{line_number}: se esperaban 5 valores")
                    continue
                cls, xc, yc, w, h = map(float, values)
                boxes.append([int(cls), xc, yc, w, h])
    return boxes


def save_labels(label_path, boxes):
    with open(label_path, "w") as f:
        for cls, xc, yc, w, h in boxes:
            f.write(f"{cls} {xc} {yc} {w} {h}\n")
# ============================
# DIBUJAR ZONAS DE EXCLUSIÓN
# ============================



def draw_exclusion_zones(img, camera_id):

    h, w = img.shape[:2]

    if camera_id not in CAMERA_CONFIG:
        return

    zones = CAMERA_CONFIG[camera_id]["exclusion_zones"]

    for z in zones:

        x1 = int(z["x1"] * w)
        y1 = int(z["y1"] * h)
        x2 = int(z["x2"] * w)
        y2 = int(z["y2"] * h)

        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            img,
            z["name"],
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )
# ============================
# DIBUJAR CAJAS Y HANDLES
# ============================

def draw_boxes(img, boxes):
    h, w, _ = img.shape

    for i, (cls, xc, yc, bw, bh) in enumerate(boxes):
        x1 = int((xc - bw/2) * w)
        y1 = int((yc - bh/2) * h)
        x2 = int((xc + bw/2) * w)
        y2 = int((yc + bh/2) * h)

        # caja
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(img, f"{i}:{CLASSES[cls]}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # handles
        handles = [
            (x1, y1),  # top-left
            (x2, y1),  # top-right
            (x1, y2),  # bottom-left
            (x2, y2)   # bottom-right
        ]

        for hx, hy in handles:
            cv2.rectangle(img,
                          (hx-HANDLE_SIZE, hy-HANDLE_SIZE),
                          (hx+HANDLE_SIZE, hy+HANDLE_SIZE),
                          (0,0,255), -1)

def draw_exclusion_zones(img, camera_id):

    if camera_id is None:
        return

    h, w = img.shape[:2]

    zones = CAMERA_CONFIG[camera_id]["exclusion_zones"]

    for zone in zones:

        x1 = int(zone["x1"] * w)
        y1 = int(zone["y1"] * h)
        x2 = int(zone["x2"] * w)
        y2 = int(zone["y2"] * h)

        # rectángulo azul
        cv2.rectangle(
            img,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        # texto de la zona
        cv2.putText(
            img,
            zone["name"],
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )
# ============================
# DETECTAR HANDLE
# ============================

def detect_handle(x, y, box, w, h):
    cls, xc, yc, bw, bh = box

    x1 = int((xc - bw/2) * w)
    y1 = int((yc - bh/2) * h)
    x2 = int((xc + bw/2) * w)
    y2 = int((yc + bh/2) * h)

    handles = {
        "tl": (x1, y1),
        "tr": (x2, y1),
        "bl": (x1, y2),
        "br": (x2, y2)
    }

    for name, (hx, hy) in handles.items():
        if abs(x - hx) <= HANDLE_SIZE and abs(y - hy) <= HANDLE_SIZE:
            return name

    return None


# ============================
# CALLBACK DEL MOUSE
# ============================

def mouse_callback(event, x, y, flags, param):
    global selected_box, selected_handle, dragging, current_boxes

    img, h, w = param

    # ajustar coordenadas por zoom
    x = int(x / zoom)
    y = int(y / zoom)

    if event == cv2.EVENT_LBUTTONDOWN:

        # detectar handle
        for i, box in enumerate(current_boxes):
            handle = detect_handle(x, y, box, w, h)
            if handle:
                selected_box = i
                selected_handle = handle
                dragging = True
                return

        # detectar clic dentro de caja (mover)
        for i, (cls, xc, yc, bw, bh) in enumerate(current_boxes):
            x1 = int((xc - bw/2) * w)
            y1 = int((yc - bh/2) * h)
            x2 = int((xc + bw/2) * w)
            y2 = int((yc + bh/2) * h)

            if x1 <= x <= x2 and y1 <= y <= y2:
                selected_box = i
                selected_handle = "move"
                dragging = True
                return

        # crear nueva caja mínima
        current_boxes.append([1, x/w, y/h, 0.01, 0.01])
        selected_box = len(current_boxes) - 1
        selected_handle = "br"
        dragging = True

    elif event == cv2.EVENT_MOUSEMOVE and dragging:

        if selected_box is None:
            return

        cls, xc, yc, bw, bh = current_boxes[selected_box]

        # mover caja
        if selected_handle == "move":
            current_boxes[selected_box][1] = x / w
            current_boxes[selected_box][2] = y / h
            return

        # redimensionar
        x1 = xc - bw/2
        y1 = yc - bh/2
        x2 = xc + bw/2
        y2 = yc + bh/2

        if selected_handle == "tl":
            x1 = x / w
            y1 = y / h
        elif selected_handle == "tr":
            x2 = x / w
            y1 = y / h
        elif selected_handle == "bl":
            x1 = x / w
            y2 = y / h
        elif selected_handle == "br":
            x2 = x / w
            y2 = y / h

        xc = (x1 + x2) / 2
        yc = (y1 + y2) / 2
        bw = abs(x2 - x1)
        bh = abs(y2 - y1)

        current_boxes[selected_box] = [cls, xc, yc, bw, bh]

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        selected_handle = None


# ============================
# EDITOR PRINCIPAL
# ============================

def main():
    global selected_box, current_boxes, zoom

    images = sorted([f for f in os.listdir(IMAGES_DIR)
                     if f.lower().endswith((".png",".jpg",".jpeg"))])

    idx = 0

    while idx < len(images):

        img_name = images[idx]
        img_path = os.path.join(IMAGES_DIR, img_name)
        label_path = os.path.join(LABELS_DIR, img_name.rsplit(".",1)[0] + ".txt")
        img = cv2.imread(img_path)
        if img is None:
            print(f"No se pudo abrir la imagen: {img_path}")
            idx += 1
            continue

        # =====================================
        # DETECTAR CAMARA SEGUN NOMBRE ARCHIVO
        # =====================================

        if "piso3" in img_name.lower():
            camera_id = "piso3"

        elif "muni" in img_name.lower():
            camera_id = "muni"

        elif "calle" in img_name.lower():
            camera_id = "calle"

        else:
            camera_id = None
        h, w, _ = img.shape

        current_boxes = load_labels(label_path)
        selected_box = None

        cv2.namedWindow("Editor YOLO")
        cv2.setMouseCallback("Editor YOLO", mouse_callback, param=(img, h, w))

        while True:

            # aplicar zoom
            zoomed = cv2.resize(img, None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LINEAR)
            display = zoomed.copy()

            draw_boxes(display, current_boxes)
            draw_exclusion_zones(display, camera_id)
            # mostrar nombre del txt
            txt_name = img_name.rsplit(".",1)[0] + ".txt"
            cv2.putText(display, txt_name, (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
            cv2.imshow("Editor YOLO", display)

            key = cv2.waitKey(20)

            # navegación
            if key == ord('n'):
                save_labels(label_path, current_boxes)
                idx += 1
                break

            if key == ord('b'):
                save_labels(label_path, current_boxes)
                idx -= 1
                if idx < 0: idx = 0
                break
            if key == ord('f'):  # forward 50
                save_labels(label_path, current_boxes)
                idx += 50
                if idx >= len(images):
                    idx = len(images) - 1
                break
            if key == ord('r'):  # rewind 50
                save_labels(label_path, current_boxes)
                idx -= 50
                if idx < 0:
                    idx = 0
                break

            # borrar caja seleccionada
            if key == ord('d'):
                if selected_box is not None:
                    current_boxes.pop(selected_box)
                    selected_box = None

            # borrar última caja creada
            if key == ord('x'):
                if len(current_boxes) > 0:
                    current_boxes.pop()
                    selected_box = None

            # cambiar clase
            if key == ord('c'):
                if selected_box is not None:
                    current_boxes[selected_box][0] = (current_boxes[selected_box][0] + 1) % len(CLASSES)

            # zoom
            if key == ord('z'):
                zoom = min(zoom + ZOOM_STEP, MAX_ZOOM)

            if key == ord('u'):
                zoom = max(zoom - ZOOM_STEP, MIN_ZOOM)

            # salir
            if key == ord('q'):
                save_labels(label_path, current_boxes)
                cv2.destroyAllWindows()
                return

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
