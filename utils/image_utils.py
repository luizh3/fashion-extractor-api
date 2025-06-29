# -*- coding: utf-8 -*-
from PIL import Image

def ensure_rgb_image(image: Image.Image) -> Image.Image:
    """
    Garante que uma imagem PIL seja RGB
    
    Args:
        image: Imagem PIL
        
    Returns:
        Imagem PIL em formato RGB
    """
    if image.mode == 'RGBA':
        # Converte RGBA para RGB com fundo branco
        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
        rgb_image.paste(image, mask=image.split()[-1])  # Usa canal alpha como máscara
        return rgb_image
    elif image.mode != 'RGB':
        # Converte outros formatos para RGB
        return image.convert('RGB')
    else:
        return image 