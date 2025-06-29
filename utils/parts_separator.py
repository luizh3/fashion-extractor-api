import cv2
import mediapipe as mp
from ultralytics import YOLO

# Inicializa MediaPipe Pose para detectar pontos do corpo
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Inicializa YOLOv8 para detectar pessoas
model = YOLO("yolov8n.pt")

def get_bounding_box(landmarks, image_width, image_height, points):
    x_coords = [landmarks[p].x * image_width for p in points]
    y_coords = [landmarks[p].y * image_height for p in points]
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    return x_min, y_min, x_max, y_max

def main(image_path):
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 1) Detecta pose com MediaPipe
    results = pose.process(image_rgb)
    if not results.pose_landmarks:
        print("Nenhuma pose detectada")
        return

    landmarks = results.pose_landmarks.landmark
    h, w, _ = image.shape

    # Define grupos de pontos para cada parte do corpo
    torso_points = [mp_pose.PoseLandmark.LEFT_SHOULDER,
                    mp_pose.PoseLandmark.RIGHT_SHOULDER,
                    mp_pose.PoseLandmark.LEFT_HIP,
                    mp_pose.PoseLandmark.RIGHT_HIP]
    legs_points = [mp_pose.PoseLandmark.LEFT_HIP,
                   mp_pose.PoseLandmark.RIGHT_HIP,
                   mp_pose.PoseLandmark.LEFT_KNEE,
                   mp_pose.PoseLandmark.RIGHT_KNEE,
                   mp_pose.PoseLandmark.LEFT_ANKLE,
                   mp_pose.PoseLandmark.RIGHT_ANKLE]
    feet_points = [mp_pose.PoseLandmark.LEFT_HEEL,
                   mp_pose.PoseLandmark.RIGHT_HEEL,
                   mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
                   mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]

    # Calcula bounding boxes
    torso_box = get_bounding_box(landmarks, w, h, torso_points)
    legs_box = get_bounding_box(landmarks, w, h, legs_points)
    feet_box = get_bounding_box(landmarks, w, h, feet_points)

    # 2) Detecta pessoas com YOLOv8
    results_yolo = model(image_path)
    # Filtra detecção de pessoa (classe 0)
    person_boxes = []
    for box in results_yolo[0].boxes:
        cls = int(box.cls[0])
        if cls == 0:  # pessoa
            xyxy = box.xyxy[0].tolist()
            person_boxes.append(xyxy)

    # Mostra imagem com boxes
    img_show = image.copy()
    # Desenha boxes do MediaPipe (partes do corpo)
    cv2.rectangle(img_show, (torso_box[0], torso_box[1]), (torso_box[2], torso_box[3]), (0, 255, 0), 2)
    cv2.putText(img_show, "Torso", (torso_box[0], torso_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.rectangle(img_show, (legs_box[0], legs_box[1]), (legs_box[2], legs_box[3]), (255, 0, 0), 2)
    cv2.putText(img_show, "Pernas", (legs_box[0], legs_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
    cv2.rectangle(img_show, (feet_box[0], feet_box[1]), (feet_box[2], feet_box[3]), (0, 0, 255), 2)
    cv2.putText(img_show, "Pés", (feet_box[0], feet_box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    # Desenha boxes do YOLO para pessoas
    for b in person_boxes:
        x1, y1, x2, y2 = map(int, b)
        cv2.rectangle(img_show, (x1,y1), (x2,y2), (0,255,255), 2)
        cv2.putText(img_show, "Pessoa", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)

    # Mostra resultado
    cv2.imwrite("resultado.jpg", img_show)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main("sua_imagem.jpg")  # troque aqui para o caminho da sua foto
