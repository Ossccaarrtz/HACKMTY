# 🌐 GUÍA: CÓMO ABRIR EL FRONTEND CORRECTAMENTE

## 📋 TU FRONTEND

Tu proyecto usa **HTML, CSS y JavaScript puros** (no React/Next.js).

Archivos principales:
```
app/frontend/
├── index.html        ← Página principal ✅
├── dashboard.html    ← Dashboard con CFO Virtual ✅
├── login.html        ← Login
├── styles.css        ← Estilos
├── main.js           ← JavaScript
└── Media/            ← Imágenes
```

---

## ✅ MÉTODO 1: SERVIDOR HTTP DE PYTHON (RECOMENDADO)

### Opción A: Python 3

```bash
# 1. Ir al directorio frontend
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend

# 2. Iniciar servidor
python -m http.server 8080

# 3. Abrir navegador
# http://localhost:8080/
```

### Opción B: Python 2 (si Python 3 no funciona)

```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend
python -m SimpleHTTPServer 8080
```

**Deberías ver:**
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

**Luego abre en navegador:**
- 🏠 **Página principal:** http://localhost:8080/index.html
- 🤖 **Dashboard con CFO:** http://localhost:8080/dashboard.html

---

## ✅ MÉTODO 2: LIVE SERVER (VS CODE)

Si usas Visual Studio Code:

### Paso 1: Instalar extensión

1. Abre VS Code
2. Ve a Extensiones (Ctrl+Shift+X)
3. Busca **"Live Server"** (de Ritwick Dey)
4. Instalar

### Paso 2: Abrir proyecto

1. File → Open Folder
2. Selecciona: `C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend`

### Paso 3: Iniciar

1. Click derecho en `index.html`
2. "Open with Live Server"
3. Se abrirá automáticamente en http://localhost:5500

---

## ✅ MÉTODO 3: DOUBLE CLICK (NO RECOMENDADO)

**⚠️ Funciona pero puede tener problemas con CORS**

Simplemente haz doble click en:
```
C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend\index.html
```

**Problema:** La URL será `file:///C:/Users/...` y puede que el backend no funcione por políticas CORS.

---

## ✅ MÉTODO 4: NODE.JS HTTP-SERVER

Si tienes Node.js instalado:

```bash
# Instalar (solo una vez)
npm install -g http-server

# Ir al directorio
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend

# Iniciar servidor
http-server -p 8080

# Abrir
# http://localhost:8080/
```

---

## 🎯 CONFIGURACIÓN COMPLETA (BACKEND + FRONTEND)

### Terminal 1: Backend

```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend
python main.py
```

**Debe mostrar:**
```
✅ Financial Advisor V3 FIXED cargado
* Running on http://127.0.0.1:8000
```

### Terminal 2: Frontend

```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend
python -m http.server 8080
```

**Debe mostrar:**
```
Serving HTTP on 0.0.0.0 port 8080
```

### Navegador:

Abrir: http://localhost:8080/dashboard.html

---

## 📄 PÁGINAS DISPONIBLES

| URL | Descripción |
|-----|-------------|
| http://localhost:8080/index.html | Página principal con KPIs y gráficas |
| http://localhost:8080/dashboard.html | Dashboard con CFO Virtual (chat) |
| http://localhost:8080/login.html | Página de login |
| http://localhost:8080/notifications-demo.html | Demo de notificaciones (si lo creaste) |

---

## 🧪 VERIFICAR QUE TODO FUNCIONA

### Test 1: Frontend cargó correctamente

1. Abre http://localhost:8080/
2. Deberías ver el logo de Banorte
3. Ver las gráficas y KPIs

### Test 2: Backend está conectado

1. Abre la consola del navegador (F12)
2. Deberías ver:
```
✅ Backend conectado
```

Si ves:
```
❌ Backend no disponible
```

→ El backend no está corriendo en puerto 8000

### Test 3: Chat funciona

1. Ve a http://localhost:8080/dashboard.html
2. Escribe: "¿Cómo está mi empresa?"
3. Debes recibir respuesta del CFO Virtual

---

## 🐛 PROBLEMAS COMUNES

### Problema 1: "Este sitio no se puede alcanzar"

**Causa:** No hay servidor corriendo

**Solución:**
```bash
cd app/frontend
python -m http.server 8080
```

### Problema 2: "Backend no disponible"

**Causa:** Backend no está corriendo

**Solución:**
```bash
# En otra terminal:
cd app/backend
python main.py
```

### Problema 3: "CORS error" en consola

**Causa:** Abriste el archivo con `file://`

**Solución:** Usa servidor HTTP (python -m http.server)

### Problema 4: "Puerto 8080 ya está en uso"

**Solución 1 - Usar otro puerto:**
```bash
python -m http.server 8081
# Luego abre: http://localhost:8081/
```

**Solución 2 - Matar proceso:**
```bash
# Windows:
netstat -ano | findstr :8080
taskkill /PID <numero> /F

# Linux/Mac:
lsof -ti:8080 | xargs kill -9
```

### Problema 5: Imágenes no cargan

**Causa:** Estructura de directorios incorrecta

**Verificar:**
```bash
ls Media/Logo.png
ls Media/icon.ico
```

Si no existen, el frontend no mostrará las imágenes correctamente.

---

## 🔧 PUERTOS RECOMENDADOS

- **Backend:** `8000`
- **Frontend:** `8080`

Estos puertos no interfieren y son fáciles de recordar.

---

## 📱 ACCESO DESDE MÓVIL (OPCIONAL)

Si quieres probar desde tu celular en la misma red:

### Paso 1: Obtener tu IP local

**Windows:**
```bash
ipconfig
# Busca "Dirección IPv4": ej. 192.168.1.100
```

**Linux/Mac:**
```bash
ifconfig | grep inet
```

### Paso 2: Iniciar servidores con 0.0.0.0

**Backend:**
```bash
# Ya está configurado en main.py:
# app.run(host="0.0.0.0", port=8000)
```

**Frontend:**
```bash
python -m http.server 8080
# Por defecto ya escucha en todas las interfaces
```

### Paso 3: Acceder desde móvil

En el navegador del celular:
```
http://192.168.1.100:8080/dashboard.html
```

(Reemplaza 192.168.1.100 con tu IP real)

---

## 📋 SCRIPT DE INICIO RÁPIDO

Crea un archivo `start.bat` (Windows) o `start.sh` (Linux/Mac):

**Windows (start.bat):**
```batch
@echo off
echo ====================================
echo   INICIANDO FINCORTEX
echo ====================================
echo.

echo [1/2] Iniciando Backend...
start /B python C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend\main.py

timeout /t 3

echo [2/2] Iniciando Frontend...
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend
start http://localhost:8080/dashboard.html
python -m http.server 8080

pause
```

**Linux/Mac (start.sh):**
```bash
#!/bin/bash
echo "===================================="
echo "   INICIANDO FINCORTEX"
echo "===================================="
echo ""

echo "[1/2] Iniciando Backend..."
cd ~/Desktop/gemini/HACKMTY/app/backend
python main.py &

sleep 3

echo "[2/2] Iniciando Frontend..."
cd ~/Desktop/gemini/HACKMTY/app/frontend
python -m http.server 8080 &

sleep 2
open http://localhost:8080/dashboard.html  # Mac
# xdg-open http://localhost:8080/dashboard.html  # Linux

echo ""
echo "✅ Todo listo!"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:8000"
echo ""
echo "Presiona Ctrl+C para detener"
wait
```

Luego solo ejecuta:
```bash
# Windows:
start.bat

# Linux/Mac:
chmod +x start.sh
./start.sh
```

---

## ✅ CHECKLIST FINAL

Antes de abrir el frontend:

- [ ] Backend corriendo en puerto 8000
- [ ] Terminal dice "Running on http://127.0.0.1:8000"
- [ ] http://localhost:8000/ responde {"status": "ok"}
- [ ] Frontend corriendo en puerto 8080
- [ ] Abrir http://localhost:8080/dashboard.html
- [ ] Ver el logo y la interfaz
- [ ] Consola del navegador (F12) sin errores
- [ ] Probar chat del CFO Virtual

---

## 🎯 COMANDO RÁPIDO (2 TERMINALES)

**Terminal 1:**
```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\backend && python main.py
```

**Terminal 2:**
```bash
cd C:\Users\Oscarin\Desktop\gemini\HACKMTY\app\frontend && python -m http.server 8080
```

**Navegador:**
```
http://localhost:8080/dashboard.html
```

---

## 🎉 TODO LISTO

Si sigues estos pasos:
1. ✅ Backend corriendo en 8000
2. ✅ Frontend corriendo en 8080
3. ✅ Dashboard abierto en navegador
4. ✅ Chat responde correctamente

**¡El sistema está completamente funcional!** 🚀

---

**¿Algún error específico que te salga al intentar abrirlo?**
