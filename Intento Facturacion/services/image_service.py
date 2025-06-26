import os
import uuid
import aiofiles
from PIL import Image
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException

class ImageService:
    """Servicio para manejo de imágenes"""
    
    def __init__(self):
        self.upload_dir = Path("static/uploads/modelos")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Tipos de archivo permitidos
        self.allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        
    def is_valid_image(self, filename: str) -> bool:
        """Verificar si el archivo es una imagen válida"""
        ext = Path(filename).suffix.lower()
        return ext in self.allowed_extensions
    
    async def save_upload_image(self, file: UploadFile) -> str:
        """Guardar imagen subida y retornar la ruta"""
        
        # Validar tipo de archivo
        if not self.is_valid_image(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Tipo de archivo no permitido. Use: JPG, PNG, GIF, WEBP"
            )
        
        # Validar tamaño
        content = await file.read()
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=400,
                detail="El archivo es muy grande. Máximo 5MB"
            )
        
        # Generar nombre único
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename
        
        try:
            # Guardar archivo
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Optimizar imagen
            await self.optimize_image(file_path)
            
            # Retornar ruta relativa
            return f"static/uploads/modelos/{unique_filename}"
            
        except Exception as e:
            # Limpiar archivo si hay error
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(
                status_code=500,
                detail=f"Error guardando imagen: {str(e)}"
            )
    
    async def optimize_image(self, file_path: Path, max_width: int = 800, quality: int = 85):
        """Optimizar imagen para web"""
        
        try:
            with Image.open(file_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Guardar optimizada
                img.save(file_path, 'JPEG', quality=quality, optimize=True)
                
        except Exception as e:
            print(f"Error optimizando imagen: {str(e)}")
    
    def delete_image(self, image_path: str) -> bool:
        """Eliminar imagen"""
        
        try:
            full_path = Path(image_path)
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error eliminando imagen: {str(e)}")
            return False
    
    def get_image_url(self, image_path: Optional[str]) -> Optional[str]:
        """Obtener URL completa de la imagen"""
        
        if not image_path:
            return None
        
        # Si ya es una URL completa, devolverla
        if image_path.startswith('http'):
            return image_path
        
        # Si es ruta relativa, construir URL
        return f"/{image_path.lstrip('/')}"

# Instancia global del servicio de imágenes
image_service = ImageService()
