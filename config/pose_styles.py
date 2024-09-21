# This file is mostly a copy of mediapipe.python.solutions.drawing_styles
# I created a copy, since editing modules is not demure at all

from typing import Mapping, Tuple

from mediapipe.python.solutions import face_mesh_connections
from mediapipe.python.solutions import hands_connections
from mediapipe.python.solutions.drawing_utils import DrawingSpec
from mediapipe.python.solutions.hands import HandLandmark as Hand
from mediapipe.python.solutions.pose import PoseLandmark as Pose


# =================================================== PIXEL  OPTIONS ===================================================
# Color palette in BGR
_RED = (48, 48, 255)
_GREEN = (48, 255, 48)
_BLUE = (192, 101, 21)
_YELLOW = (0, 204, 255)
_GRAY = (128, 128, 128)
_PURPLE = (128, 64, 128)
_PEACH = (180, 229, 255)
_WHITE = (224, 224, 224)
_CYAN = (192, 255, 48)
_MAGENTA = (192, 48, 255)

# Hands options
_THICKNESS_WRIST_MCP = 1
_THICKNESS_FINGER = 1
_THICKNESS_DOT = -1
_RADIUS_DOT = 3

# Face mesh options
_THICKNESS_TESSELATION = 1
_THICKNESS_CONTOURS = 1

# Pose options
_THICKNESS_POSE_LANDMARKS = 1


# ========================================== LANDMARK AND CONNECTIONS OPTIONS ==========================================
_PALM_LANDMARKS = (Hand.WRIST, Hand.THUMB_CMC, Hand.INDEX_FINGER_MCP,
                   Hand.MIDDLE_FINGER_MCP, Hand.RING_FINGER_MCP, Hand.PINKY_MCP)
_THUMB_LANDMARKS = (Hand.THUMB_MCP, Hand.THUMB_IP, Hand.THUMB_TIP)
_INDEX_FINGER_LANDMARKS = (Hand.INDEX_FINGER_PIP, Hand.INDEX_FINGER_DIP, Hand.INDEX_FINGER_TIP)
_MIDDLE_FINGER_LANDMARKS = (Hand.MIDDLE_FINGER_PIP, Hand.MIDDLE_FINGER_DIP, Hand.MIDDLE_FINGER_TIP)
_RING_FINGER_LANDMARKS = (Hand.RING_FINGER_PIP, Hand.RING_FINGER_DIP, Hand.RING_FINGER_TIP)
_PINKY_FINGER_LANDMARKS = (Hand.PINKY_PIP, Hand.PINKY_DIP, Hand.PINKY_TIP)

_POSE_LANDMARKS_LEFT = frozenset([
    Pose.LEFT_EYE_INNER, Pose.LEFT_EYE, Pose.LEFT_EYE_OUTER, Pose.LEFT_EAR, Pose.MOUTH_LEFT,
    Pose.LEFT_SHOULDER, Pose.LEFT_ELBOW, Pose.LEFT_WRIST, Pose.LEFT_PINKY, Pose.LEFT_INDEX, Pose.LEFT_THUMB,
    Pose.LEFT_HIP, Pose.LEFT_KNEE, Pose.LEFT_ANKLE, Pose.LEFT_HEEL, Pose.LEFT_FOOT_INDEX
])

_POSE_LANDMARKS_RIGHT = frozenset([
    Pose.RIGHT_EYE_INNER, Pose.RIGHT_EYE, Pose.RIGHT_EYE_OUTER, Pose.RIGHT_EAR, Pose.MOUTH_RIGHT,
    Pose.RIGHT_SHOULDER, Pose.RIGHT_ELBOW, Pose.RIGHT_WRIST, Pose.RIGHT_PINKY, Pose.RIGHT_INDEX, Pose.RIGHT_THUMB,
    Pose.RIGHT_HIP, Pose.RIGHT_KNEE, Pose.RIGHT_ANKLE, Pose.RIGHT_HEEL, Pose.RIGHT_FOOT_INDEX
])


# ======================================= LANDMARK AND CONNECTIONS COLOR OPTIONS =======================================
_HAND_LANDMARK_STYLE = {
    _PALM_LANDMARKS:            DrawingSpec(color=_RED, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
    _THUMB_LANDMARKS:           DrawingSpec(color=_PEACH, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
    _INDEX_FINGER_LANDMARKS:    DrawingSpec(color=_PURPLE, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
    _MIDDLE_FINGER_LANDMARKS:   DrawingSpec(color=_YELLOW, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
    _RING_FINGER_LANDMARKS:     DrawingSpec(color=_GREEN, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
    _PINKY_FINGER_LANDMARKS:    DrawingSpec(color=_BLUE, thickness=_THICKNESS_DOT, circle_radius=_RADIUS_DOT),
}

_HAND_CONNECTION_STYLE = {
    hands_connections.HAND_PALM_CONNECTIONS:            DrawingSpec(color=_GRAY, thickness=_THICKNESS_WRIST_MCP),
    hands_connections.HAND_THUMB_CONNECTIONS:           DrawingSpec(color=_PEACH, thickness=_THICKNESS_FINGER),
    hands_connections.HAND_INDEX_FINGER_CONNECTIONS:    DrawingSpec(color=_PURPLE, thickness=_THICKNESS_FINGER),
    hands_connections.HAND_MIDDLE_FINGER_CONNECTIONS:   DrawingSpec(color=_YELLOW, thickness=_THICKNESS_FINGER),
    hands_connections.HAND_RING_FINGER_CONNECTIONS:     DrawingSpec(color=_GREEN, thickness=_THICKNESS_FINGER),
    hands_connections.HAND_PINKY_FINGER_CONNECTIONS:    DrawingSpec(color=_BLUE, thickness=_THICKNESS_FINGER)
}

_FACEMESH_CONTOURS_CONNECTION_STYLE = {
    face_mesh_connections.FACEMESH_LIPS:            DrawingSpec(color=_BLUE, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_LEFT_EYE:        DrawingSpec(color=_CYAN, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_LEFT_EYEBROW:    DrawingSpec(color=_GREEN, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_RIGHT_EYE:       DrawingSpec(color=_MAGENTA, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_RIGHT_EYEBROW:   DrawingSpec(color=_RED, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_FACE_OVAL:       DrawingSpec(color=_WHITE, thickness=_THICKNESS_CONTOURS),
    face_mesh_connections.FACEMESH_NOSE:            DrawingSpec(color=_YELLOW, thickness=_THICKNESS_CONTOURS)
}


# ================================================= MAPPING  FUNCTIONS =================================================
def get_hand_landmarks_style() -> Mapping[int, DrawingSpec]:
    hand_landmark_style = {}
    for k, v in _HAND_LANDMARK_STYLE.items():
        for landmark in k:
            hand_landmark_style[landmark] = v
    return hand_landmark_style


def get_hand_connections_style() -> Mapping[Tuple[int, int], DrawingSpec]:
    hand_connection_style = {}
    for k, v in _HAND_CONNECTION_STYLE.items():
        for connection in k:
            hand_connection_style[connection] = v
    return hand_connection_style


def get_face_mesh_contours_style() -> Mapping[Tuple[int, int], DrawingSpec]:
    default_style = _FACEMESH_CONTOURS_CONNECTION_STYLE

    face_mesh_contours_connection_style = {}
    for k, v in default_style.items():
        for connection in k:
            face_mesh_contours_connection_style[connection] = v
    return face_mesh_contours_connection_style


def get_face_mesh_tesselation_style() -> DrawingSpec:
    return DrawingSpec(color=_GRAY, thickness=_THICKNESS_TESSELATION)


def get_face_mesh_iris_connections_style() -> Mapping[Tuple[int, int], DrawingSpec]:
    face_mesh_iris_connections_style = {}
    left_spec = DrawingSpec(color=_GREEN, thickness=_THICKNESS_CONTOURS)
    for connection in face_mesh_connections.FACEMESH_LEFT_IRIS:
        face_mesh_iris_connections_style[connection] = left_spec
    right_spec = DrawingSpec(color=_RED, thickness=_THICKNESS_CONTOURS)
    for connection in face_mesh_connections.FACEMESH_RIGHT_IRIS:
        face_mesh_iris_connections_style[connection] = right_spec
    return face_mesh_iris_connections_style


def get_pose_landmarks_style() -> Mapping[int, DrawingSpec]:
    pose_landmark_style = {}
    left_spec = DrawingSpec(
        color=(0, 138, 255), thickness=_THICKNESS_POSE_LANDMARKS)
    right_spec = DrawingSpec(
        color=(231, 217, 0), thickness=_THICKNESS_POSE_LANDMARKS)
    for landmark in _POSE_LANDMARKS_LEFT:
        pose_landmark_style[landmark] = left_spec
    for landmark in _POSE_LANDMARKS_RIGHT:
        pose_landmark_style[landmark] = right_spec
    pose_landmark_style[Pose.NOSE] = DrawingSpec(
        color=_WHITE, thickness=_THICKNESS_POSE_LANDMARKS)
    return pose_landmark_style
