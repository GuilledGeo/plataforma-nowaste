"""
Script de prueba para escanear el ticket de Mercadona
"""
from app.services.ticket_scanner_service import TicketScannerService
import json

# ⭐ Pon la imagen en la misma carpeta del proyecto
ticket_path = r"E:\0_Proyectos\1_nowaste\freshkeep-backend\ticket_mercadona.jpeg"

# Crear servicio
scanner = TicketScannerService()

# Procesar
print("🔄 Escaneando ticket...")
result = scanner.process_ticket(ticket_path)

# Mostrar resultados
print("\n" + "="*60)
print(f"✅ RESULTADO DEL ESCANEO")
print("="*60)
print(f"🏪 Tienda: {result['store']}")
print(f"📅 Fecha: {result['purchase_date']}")
print(f"📦 Productos encontrados: {result['total_products']}\n")

for i, product in enumerate(result['products'], 1):
    print(f"{i}. {product['name']}")
    print(f"   💰 Precio: €{product['price']:.2f}")
    print(f"   📂 Categoría: {product['category']}")
    print(f"   📍 Ubicación: {product['location']}")
    print(f"   ⏰ Caduca: {product['expiration_date'][:10]}")
    print()

# Guardar resultado en JSON
with open('resultado_scan.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("💾 Resultado guardado en: resultado_scan.json")