import cv2
import numpy as np

# Rangos de rojo en HSV
LOWER_RED_1 = np.array([0, 80, 80])
UPPER_RED_1 = np.array([10, 255, 255])

LOWER_RED_2 = np.array([160, 80, 80])
UPPER_RED_2 = np.array([180, 255, 255])


def red_mask(bgr_roi):
    """Devuelve la máscara binaria de píxeles rojos."""
    hsv = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, LOWER_RED_1, UPPER_RED_1)
    mask2 = cv2.inRange(hsv, LOWER_RED_2, UPPER_RED_2)
    return cv2.bitwise_or(mask1, mask2)


def is_red_vehicle(bgr_roi,
                   ratio_threshold=0.12,
                   spread_threshold=0.25):
    """
    Detecta si un vehículo es rojo usando:
    - ratio de píxeles rojos
    - distribución espacial del rojo (spread)
    
    ratio_threshold: mínimo porcentaje de rojo
    spread_threshold: mínimo ancho/alto relativo del área roja
    """

    if bgr_roi is None or bgr_roi.size == 0:
        return False

    mask = red_mask(bgr_roi)

    # Ratio de rojo
    red_ratio = np.count_nonzero(mask) / mask.size
    if red_ratio < ratio_threshold:
        return False

    # Distribución del rojo (spread)
    ys, xs = np.where(mask > 0)
    if len(xs) == 0:
        return False

    spread_x = (xs.max() - xs.min()) / bgr_roi.shape[1]
    spread_y = (ys.max() - ys.min()) / bgr_roi.shape[0]
    spread = max(spread_x, spread_y)

    # Si el rojo está distribuido → auto rojo
    # Si está concentrado en un punto → luz de freno
    return spread >= spread_threshold
