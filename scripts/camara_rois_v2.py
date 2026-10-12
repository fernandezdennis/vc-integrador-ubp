# camara_rois_v2.py

from math import sqrt

from referencias_urbanas import REFERENCIAS_URBANAS


CAMERA_CONFIG = {

    "muni": {

        "exclusion_zones": [

            {
                "name": "CONTENEDOR_OBRA",
                "x1": 0.76,
                "y1": 0.46,
                "x2": 0.80,
                "y2": 0.51
            }

        ]
    },

    "piso3": {

        "exclusion_zones": [

            {
                "name": "CONTENEDOR_OBRA",
                "x1": 0.07,
                "y1": 0.40,
                "x2": 0.14,
                "y2": 0.50
            }

        ]
    },

    "calle": {

        "exclusion_zones": []

    }
}


def inside_exclusion_zone(camera_id, xc, yc):

    zones = CAMERA_CONFIG[camera_id].get(
        "exclusion_zones",
        []
    )

    for z in zones:

        if (
            z["x1"] <= xc <= z["x2"]
            and
            z["y1"] <= yc <= z["y2"]
        ):
            return True

    return False


def point_distance(x1, y1, x2, y2):

    return sqrt(
        (x1 - x2) ** 2 +
        (y1 - y2) ** 2
    )


def point_to_segment_distance(
    px,
    py,
    x1,
    y1,
    x2,
    y2
):

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:

        return point_distance(
            px, py,
            x1, y1
        )

    t = (
        (px - x1) * dx +
        (py - y1) * dy
    ) / (
        dx * dx +
        dy * dy
    )

    t = max(
        0,
        min(
            1,
            t
        )
    )

    proj_x = x1 + t * dx
    proj_y = y1 + t * dy

    return point_distance(
        px,
        py,
        proj_x,
        proj_y
    )


def get_reference(
    camera_id,
    xc,
    yc
):

    refs = REFERENCIAS_URBANAS[camera_id]

    best_name = None
    best_dist = 999

    for ref in refs:

        if ref["type"] == "point":

            dist = point_distance(
                xc,
                yc,
                ref["cx"],
                ref["cy"]
            )

            threshold = ref["radius"]

        else:

            dist = point_to_segment_distance(

                xc,
                yc,

                ref["x1"],
                ref["y1"],

                ref["x2"],
                ref["y2"]
            )

            threshold = ref["distance"]

        if dist <= threshold:

            if dist < best_dist:

                best_dist = dist
                best_name = ref["name"]

    return best_name


def get_near_references(
    camera_id,
    xc,
    yc
):

    refs = REFERENCIAS_URBANAS[camera_id]

    matches = []

    for ref in refs:

        if ref["type"] == "point":

            dist = point_distance(
                xc,
                yc,
                ref["cx"],
                ref["cy"]
            )

            threshold = ref["radius"]

        else:

            dist = point_to_segment_distance(

                xc,
                yc,

                ref["x1"],
                ref["y1"],

                ref["x2"],
                ref["y2"]
            )

            threshold = ref["distance"]

        if dist <= threshold:

            matches.append(
                ref["name"]
            )

    return matches
