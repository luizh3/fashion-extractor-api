import cv2
import mediapipe as mp
from ultralytics import YOLO
from PIL import Image
import numpy as np
from typing import Dict, List, Tuple, Optional

class BodyPartsDetector:
    """Classe para detectar partes do corpo usando MediaPipe e YOLO"""
    
    def __init__(self, margin_percentage: float = 0.30):
        """
        Inicializa os modelos de detecção
        
        Args:
            margin_percentage: Percentual de margem para expandir as bounding boxes (0.30 = 30%)
        """
        # Inicializa MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True, 
            min_detection_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Inicializa YOLOv8
        self.yolo_model = YOLO("yolov8n.pt")
        
        # Margem de tolerância
        self.margin_percentage = margin_percentage
        
        # Define grupos de pontos para cada parte do corpo
        self.torso_points = [
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP
        ]
        
        self.legs_points = [
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
            self.mp_pose.PoseLandmark.LEFT_KNEE,
            self.mp_pose.PoseLandmark.RIGHT_KNEE,
            self.mp_pose.PoseLandmark.LEFT_ANKLE,
            self.mp_pose.PoseLandmark.RIGHT_ANKLE
        ]
        
        self.feet_points = [
            self.mp_pose.PoseLandmark.LEFT_HEEL,
            self.mp_pose.PoseLandmark.RIGHT_HEEL,
            self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX,
            self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX
        ]
    
    def _get_bounding_box_with_margin(self, landmarks, image_width: int, image_height: int, points: List) -> Tuple[int, int, int, int]:
        """
        Calcula bounding box para um grupo de pontos com margem de tolerância
        
        Args:
            landmarks: Landmarks do MediaPipe
            image_width: Largura da imagem
            image_height: Altura da imagem
            points: Lista de pontos para calcular o box
            
        Returns:
            Tupla (x_min, y_min, x_max, y_max) com margem
        """
        x_coords = [landmarks[p].x * image_width for p in points]
        y_coords = [landmarks[p].y * image_height for p in points]
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        
        # Calcula margem baseada no tamanho da bounding box
        width = x_max - x_min
        height = y_max - y_min
        margin_x = int(width * self.margin_percentage)
        margin_y = int(height * self.margin_percentage)
        
        # Aplica margem (garantindo que não saia dos limites da imagem)
        x_min = max(0, x_min - margin_x)
        y_min = max(0, y_min - margin_y)
        x_max = min(image_width, x_max + margin_x)
        y_max = min(image_height, y_max + margin_y)
        
        return x_min, y_min, x_max, y_max
    
    def _get_bounding_box(self, landmarks, image_width: int, image_height: int, points: List) -> Tuple[int, int, int, int]:
        """
        Calcula bounding box para um grupo de pontos (sem margem - mantido para compatibilidade)
        
        Args:
            landmarks: Landmarks do MediaPipe
            image_width: Largura da imagem
            image_height: Altura da imagem
            points: Lista de pontos para calcular o box
            
        Returns:
            Tupla (x_min, y_min, x_max, y_max)
        """
        x_coords = [landmarks[p].x * image_width for p in points]
        y_coords = [landmarks[p].y * image_height for p in points]
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))
        return x_min, y_min, x_max, y_max
    
    def _ensure_rgb_image(self, image: np.ndarray) -> np.ndarray:
        """
        Garante que a imagem seja RGB (3 canais)
        
        Args:
            image: Imagem como numpy array
            
        Returns:
            Imagem RGB como numpy array
        """
        if len(image.shape) == 3:
            if image.shape[2] == 4:  # RGBA
                # Converte RGBA para RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            elif image.shape[2] == 3:  # RGB
                image_rgb = image
            else:
                # Se for outro formato, converte para RGB
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            # Se for grayscale, converte para RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        return image_rgb
    
    def detect_body_parts(self, image: np.ndarray) -> Dict:
        """
        Detecta partes do corpo na imagem
        
        Args:
            image: Imagem como numpy array (BGR)
            
        Returns:
            Dicionário com as detecções
        """
        # Garante que a imagem seja RGB
        image_rgb = self._ensure_rgb_image(image)
        h, w, _ = image_rgb.shape
        
        # 1) Detecta pose com MediaPipe
        results = self.pose.process(image_rgb)
        
        if not results.pose_landmarks:
            return {
                "success": False,
                "error": "Nenhuma pose detectada",
                "body_parts": {},
                "people": []
            }
        
        landmarks = results.pose_landmarks.landmark
        
        # Calcula bounding boxes das partes do corpo COM margem
        torso_box = self._get_bounding_box_with_margin(landmarks, w, h, self.torso_points)
        legs_box = self._get_bounding_box_with_margin(landmarks, w, h, self.legs_points)
        feet_box = self._get_bounding_box_with_margin(landmarks, w, h, self.feet_points)
        
        # 2) Detecta pessoas com YOLOv8 (usa a imagem RGB)
        results_yolo = self.yolo_model(image_rgb)
        person_boxes = []
        
        for box in results_yolo[0].boxes:
            cls = int(box.cls[0])
            if cls == 0:  # pessoa
                xyxy = box.xyxy[0].tolist()
                person_boxes.append(xyxy)
        
        # Prepara resultado
        body_parts = {
            "torso": {
                "bbox": torso_box,
                "area": (torso_box[2] - torso_box[0]) * (torso_box[3] - torso_box[1])
            },
            "legs": {
                "bbox": legs_box,
                "area": (legs_box[2] - legs_box[0]) * (legs_box[3] - legs_box[1])
            },
            "feet": {
                "bbox": feet_box,
                "area": (feet_box[2] - feet_box[0]) * (feet_box[3] - feet_box[1])
            }
        }
        
        return {
            "success": True,
            "body_parts": body_parts,
            "people": person_boxes,
            "image_dimensions": {"width": w, "height": h}
        }
    
    def detect_from_pil(self, pil_image: Image.Image) -> Dict:
        """
        Detecta partes do corpo a partir de uma imagem PIL
        
        Args:
            pil_image: Imagem PIL
            
        Returns:
            Dicionário com as detecções
        """
        # Converte PIL para numpy array e garante formato RGB
        if pil_image.mode == 'RGBA':
            # Converte RGBA para RGB
            pil_image = pil_image.convert('RGB')
        elif pil_image.mode != 'RGB':
            # Converte outros formatos para RGB
            pil_image = pil_image.convert('RGB')
        
        # Converte para numpy array
        image_np = np.array(pil_image)
        
        # Garante que seja RGB (3 canais)
        image_rgb = self._ensure_rgb_image(image_np)
        
        return self.detect_body_parts(image_rgb)
    
    def get_body_part_image(self, pil_image: Image.Image, part_name: str) -> Optional[Image.Image]:
        """
        Extrai uma parte específica do corpo da imagem
        
        Args:
            pil_image: Imagem PIL original
            part_name: Nome da parte ('torso', 'legs', 'feet')
            
        Returns:
            Imagem PIL da parte do corpo ou None se não encontrada
        """
        detection = self.detect_from_pil(pil_image)
        
        if not detection["success"] or part_name not in detection["body_parts"]:
            return None
        
        bbox = detection["body_parts"][part_name]["bbox"]
        x_min, y_min, x_max, y_max = bbox
        
        # Extrai a região da imagem
        part_image = pil_image.crop((x_min, y_min, x_max, y_max))
        return part_image
    
    def set_margin_percentage(self, margin_percentage: float):
        """
        Define a margem de tolerância
        
        Args:
            margin_percentage: Percentual de margem (0.1 = 10%, 0.2 = 20%, etc.)
        """
        self.margin_percentage = max(0.0, min(1.0, margin_percentage))  # Limita entre 0% e 100%

# Instância global do detector
detector = BodyPartsDetector()

def detect_body_parts_from_image(image: Image.Image) -> Dict:
    """
    Função utilitária para detectar partes do corpo
    
    Args:
        image: Imagem PIL
        
    Returns:
        Dicionário com as detecções
    """
    return detector.detect_from_pil(image)

def get_body_part_image(image: Image.Image, part_name: str) -> Optional[Image.Image]:
    """
    Função utilitária para extrair parte do corpo
    
    Args:
        image: Imagem PIL
        part_name: Nome da parte ('torso', 'legs', 'feet')
        
    Returns:
        Imagem PIL da parte ou None
    """
    return detector.get_body_part_image(image, part_name)

def set_margin_percentage(margin_percentage: float):
    """
    Função utilitária para definir margem de tolerância
    
    Args:
        margin_percentage: Percentual de margem (0.1 = 10%, 0.2 = 20%, etc.)
    """
    detector.set_margin_percentage(margin_percentage)

def get_margin_percentage() -> float:
    """
    Função utilitária para obter a margem de tolerância atual
    
    Returns:
        Percentual de margem atual (0.1 = 10%, 0.2 = 20%, etc.)
    """
    return detector.margin_percentage 