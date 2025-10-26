# 🚀 GUÍA: CÓMO EJECUTAR EL BACKEND CORRECTAMENTE

## 📋 ESTRUCTURA DEL PROYECTO

Tu proyecto tiene **2 backends diferentes**:

```
app/
├── backend/           ← ✅ BACKEND PRINCIPAL (ESTE ES EL CORRECTO)
│   ├── main.py       ← Archivo principal
│   ├── modules/
│   │   └── financial_advisor_v3_fixed.py
│   └── data/
│
└── cfo_voice/        ← ⚠️ Backend antiguo (NO usar)
    └── main.py
```

---

## ✅ FORMA CORRECTA DE EJECUTAR

### PASO 1: Ubicarte en el directorio correcto

```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend
```

**IMPORTANTE:** Debes estar en `app/backend/`, NO en `app/cfo_voice/`

### PASO 2: Verificar archivos necesarios

```bash
# Verificar que existen estos archivos:
ls main.py                                    # ✅ Debe existir
ls modules/financial_advisor_v3_fixed.py     # ✅ Debe existir
ls data/internos/finanzas_empresa_limpio.csv # ✅ Debe existir
```

### PASO 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:
```bash
pip install flask flask-cors python-dotenv google-generativeai gtts speechrecognition pydub pandas numpy
```

### PASO 4: Verificar variables de entorno

Asegúrate que existe un archivo `.env` en `app/backend/`:

```bash
# Verificar:
cat .env
```

Debe contener:
```env
GEMINI_API_KEY=tu_api_key_aqui
```

Si no existe, créalo:
```bash
echo GEMINI_API_KEY=AIzaSy... > .env
```

### PASO 5: Ejecutar el backend

```bash
python main.py
```

**Deberías ver:**
```
[System] ✅ Financial Advisor V3 FIXED cargado
[FinAdvisor] ✅ Datos cargados
   📊 Empresas disponibles: 50
   👤 Usuarios disponibles: 100
   🎯 Empresa actual: E005
   🎯 Usuario actual: 47

 * Serving Flask app 'main'
 * Debug mode: off
WARNING: This is a development server.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://192.168.x.x:8000
```

---

## 🧪 VERIFICAR QUE FUNCIONA

### Test 1: Verificar que el servidor responde

Abre otra terminal y ejecuta:
```bash
curl http://localhost:8000/
```

**Debería responder:**
```json
{
  "status": "ok",
  "version": "..."
}
```

### Test 2: Probar el chat

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"¿Cómo está mi empresa?\"}"
```

**Debería responder con:**
```json
{
  "text": "Tu empresa E005 está en estado BUENO...",
  "audio_base64": "...",
  "processing_time": "2.34s"
}
```

### Test 3: Verificar análisis financiero

```bash
curl http://localhost:8000/api/finanzas/estado
```

**Debe mostrar:**
```json
{
  "success": true,
  "empresa": {
    "empresa_id": "E005",
    "margen": 16.6,
    "estado": "BUENO",
    ...
  }
}
```

---

## ⚠️ ERRORES COMUNES

### Error 1: "ModuleNotFoundError: No module named 'modules'"

**Causa:** Estás en el directorio incorrecto

**Solución:**
```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend
python main.py
```

### Error 2: "ModuleNotFoundError: No module named 'flask'"

**Causa:** Dependencias no instaladas

**Solución:**
```bash
pip install flask flask-cors
```

### Error 3: "FileNotFoundError: finanzas_empresa_limpio.csv"

**Causa:** Archivos de datos no existen

**Solución:**
```bash
# Verificar que existen:
ls data/internos/finanzas_empresa_limpio.csv
ls data/internos/finanzas_personales_limpio.csv
```

### Error 4: "Address already in use"

**Causa:** El puerto 8000 ya está ocupado

**Solución 1 - Matar el proceso:**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <numero_pid> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

**Solución 2 - Usar otro puerto:**
```bash
# En main.py, cambiar:
app.run(host="0.0.0.0", port=8000)
# Por:
app.run(host="0.0.0.0", port=8001)
```

### Error 5: "Financial advisor no disponible"

**Causa:** El archivo `financial_advisor_v3_fixed.py` no existe

**Solución:**
```bash
# Verificar:
ls modules/financial_advisor_v3_fixed.py

# Si no existe, está en la raíz del proyecto como:
# financial_advisor_v3_fixed.py
# Cópialo a modules/
```

---

## 📊 PUERTOS UTILIZADOS

- **Backend Principal:** `http://localhost:8000`
- **Frontend:** `http://localhost:8080` (o donde lo sirvas)

---

## 🔧 COMANDOS ÚTILES

### Ver logs en tiempo real:
```bash
python main.py
# Deja esta terminal abierta para ver los logs
```

### Ejecutar en background (Linux/Mac):
```bash
nohup python main.py > backend.log 2>&1 &
```

### Ejecutar en background (Windows):
```powershell
Start-Process python -ArgumentList "main.py" -WindowStyle Hidden
```

### Ver si está corriendo:
```bash
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i:8000
```

---

## 📁 ESTRUCTURA COMPLETA

```
app/backend/
├── main.py                          ← Ejecutar este
├── .env                             ← API keys
├── requirements.txt                 ← Dependencias
├── modules/
│   ├── financial_advisor_v3_fixed.py  ← Análisis correcto
│   └── prophet_engine.py            ← Predicciones
├── data/
│   ├── internos/
│   │   ├── finanzas_empresa_limpio.csv
│   │   └── finanzas_personales_limpio.csv
│   └── externos/
└── uploads/
```

---

## 🎯 CHECKLIST FINAL

Antes de ejecutar, verifica:

- [ ] Estás en `app/backend/` (no en `cfo_voice/`)
- [ ] Existe `main.py` en este directorio
- [ ] Existe `modules/financial_advisor_v3_fixed.py`
- [ ] Existe `.env` con `GEMINI_API_KEY`
- [ ] Existen los CSVs en `data/internos/`
- [ ] Dependencias instaladas (`pip list | grep flask`)
- [ ] Puerto 8000 libre
- [ ] Python 3.8 o superior (`python --version`)

---

## 🚀 COMANDO FINAL

```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend
python main.py
```

**Si todo está bien, verás:**
```
✅ Financial Advisor V3 FIXED cargado
✅ Datos cargados
🎯 Empresa actual: E005
* Running on http://127.0.0.1:8000
```

**Ahora puedes abrir tu frontend y el chat funcionará correctamente.** 🎉

---

## 🆘 SI NADA FUNCIONA

Ejecuta este script de diagnóstico:

```bash
python << 'EOF'
import os
import sys

print("="*60)
print("🔍 DIAGNÓSTICO DEL BACKEND")
print("="*60)

# 1. Directorio actual
print(f"\n📁 Directorio actual: {os.getcwd()}")
correcto = "app\\backend" in os.getcwd() or "app/backend" in os.getcwd()
print(f"   {'✅' if correcto else '❌'} {'Correcto' if correcto else 'INCORRECTO - Cambia a app/backend'}")

# 2. Archivos principales
archivos = [
    'main.py',
    'modules/financial_advisor_v3_fixed.py',
    'data/internos/finanzas_empresa_limpio.csv',
    '.env'
]

print("\n📄 Archivos necesarios:")
for archivo in archivos:
    existe = os.path.exists(archivo)
    print(f"   {'✅' if existe else '❌'} {archivo}")

# 3. Módulos Python
print("\n📦 Módulos Python:")
modulos = ['flask', 'pandas', 'google.generativeai']
for modulo in modulos:
    try:
        __import__(modulo)
        print(f"   ✅ {modulo}")
    except:
        print(f"   ❌ {modulo} (pip install {modulo})")

# 4. Puerto 8000
print("\n🌐 Puerto 8000:")
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 8000))
if result == 0:
    print("   ⚠️  Ya está en uso (detén el proceso anterior)")
else:
    print("   ✅ Disponible")
sock.close()

print("\n" + "="*60)
EOF
```

Esto te dirá exactamente qué está mal.

---

**¿Necesitas ayuda con algún error específico que te salga al ejecutar?**
