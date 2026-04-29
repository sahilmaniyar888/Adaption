"""MediaPipe Holistic landmark extraction pipeline.

Produces per-clip `.npy` arrays shaped (T, 543, 3) that are directly
ingestable by transformer Sign-to-Text models (e.g. SignBERT, MMSign,
OpenHands). Layout per frame:

    indices  0..32     -> Pose (33 landmarks)
    indices 33..500    -> Face (468 landmarks)
    indices 501..521   -> Left hand (21 landmarks)
    indices 522..542   -> Right hand (21 landmarks)
    Total:               543 landmarks per frame, (x, y, z) each.

Missing landmarks are filled with zeros (standard practice — masked at
training time). The signer bounding box is also returned so the schema's
`bounding_box` field can be populated.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    import cv2  # type: ignore
    import mediapipe as mp  # type: ignore
    import numpy as np  # type: ignore
    _CV_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dep
    _CV_AVAILABLE = False


POSE_N = 33
FACE_N = 468
HAND_N = 21
TOTAL_N = POSE_N + FACE_N + HAND_N + HAND_N  # 543


@dataclass(slots=True)
class ExtractionResult:
    landmarks: "np.ndarray"           # (T, 543, 3)
    bbox: tuple[float, float, float, float]  # (x, y, w, h) in [0,1]
    fps: float
    frame_count: int


def _require_cv() -> None:
    if not _CV_AVAILABLE:
        raise ImportError(
            "MediaPipe pipeline needs the 'cv' extras. Install with:\n"
            "    pip install -e .[cv]"
        )


def _frames(video_path: Path) -> Iterator["np.ndarray"]:
    cap = cv2.VideoCapture(str(video_path))
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                return
            yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    finally:
        cap.release()


def _stack_landmarks(result) -> "np.ndarray":
    """Flatten one Holistic result into (543, 3). Missing parts -> zeros."""
    out = np.zeros((TOTAL_N, 3), dtype=np.float32)

    if result.pose_landmarks:
        for i, lm in enumerate(result.pose_landmarks.landmark):
            out[i] = (lm.x, lm.y, lm.z)

    if result.face_landmarks:
        offset = POSE_N
        for i, lm in enumerate(result.face_landmarks.landmark):
            out[offset + i] = (lm.x, lm.y, lm.z)

    if result.left_hand_landmarks:
        offset = POSE_N + FACE_N
        for i, lm in enumerate(result.left_hand_landmarks.landmark):
            out[offset + i] = (lm.x, lm.y, lm.z)

    if result.right_hand_landmarks:
        offset = POSE_N + FACE_N + HAND_N
        for i, lm in enumerate(result.right_hand_landmarks.landmark):
            out[offset + i] = (lm.x, lm.y, lm.z)

    return out


def _signer_bbox(landmarks: "np.ndarray") -> tuple[float, float, float, float]:
    """Tightest [x, y, w, h] (normalised) box around all non-zero landmarks
    across all frames — used to crop the signer for downstream visual models.
    """
    nonzero = landmarks[(landmarks != 0).any(axis=-1)]
    if nonzero.size == 0:
        return (0.0, 0.0, 1.0, 1.0)
    xs, ys = nonzero[:, 0], nonzero[:, 1]
    x0, x1 = float(xs.min()), float(xs.max())
    y0, y1 = float(ys.min()), float(ys.max())
    pad = 0.05
    x0 = max(0.0, x0 - pad)
    y0 = max(0.0, y0 - pad)
    x1 = min(1.0, x1 + pad)
    y1 = min(1.0, y1 + pad)
    return (x0, y0, max(1e-3, x1 - x0), max(1e-3, y1 - y0))


def extract(video_path: Path) -> ExtractionResult:
    """Run MediaPipe Holistic over a video and return packed landmarks."""
    _require_cv()

    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()

    holistic = mp.solutions.holistic.Holistic(
        static_image_mode=False,
        model_complexity=1,
        smooth_landmarks=True,
        refine_face_landmarks=False,
    )
    try:
        per_frame = []
        for frame in _frames(video_path):
            result = holistic.process(frame)
            per_frame.append(_stack_landmarks(result))
        if not per_frame:
            raise RuntimeError(f"No frames decoded from {video_path}")
        arr = np.stack(per_frame, axis=0)  # (T, 543, 3)
    finally:
        holistic.close()

    return ExtractionResult(
        landmarks=arr,
        bbox=_signer_bbox(arr),
        fps=float(fps),
        frame_count=int(arr.shape[0]),
    )


def extract_and_save(video_path: Path, out_path: Path) -> ExtractionResult:
    """Convenience wrapper that writes the (T, 543, 3) array to `.npy`."""
    res = extract(video_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(out_path, res.landmarks)
    return res
