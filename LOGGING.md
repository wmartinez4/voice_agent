# 📊 Sistema de Logging

Sistema de logging similar a **Serilog (.NET)** implementado en Python con múltiples outputs.

---

## 📂 Estructura de Logs

```
logs/
├── app_YYYYMMDD.log       # Todos los logs (INFO + DEBUG)
└── errors_YYYYMMDD.log    # Solo errores (ERROR + CRITICAL)
```

### Ejemplo:
```
logs/
├── app_20251125.log       # Logs generales del 25 de noviembre
└── errors_20251125.log    # Errores del 25 de noviembre
```

---

## 🎯 Características

### ✅ Múltiples Outputs (Como Serilog Sinks)

| Output | Nivel | Descripción |
|--------|-------|-------------|
| **Console** | INFO+ | Para desarrollo y debugging en tiempo real |
| **app_*.log** | INFO+ | Registro completo de operaciones |
| **errors_*.log** | ERROR+ | Solo errores para análisis rápido |

### ✅ Rotation Automática

- **Tamaño máximo**: 10MB por archivo
- **Backups**: Mantiene 5 archivos históricos
- **Formato**: `app_20251125.log`, `app_20251125.log.1`, `app_20251125.log.2`...

### ✅ Formato Estructurado

```
YYYY-MM-DD HH:MM:SS | LEVEL    | LOGGER | MESSAGE
2025-11-25 20:55:06 | INFO     | main   | ✅ Customer name retrieved: Willian Martinez
```

---

## 📊 Niveles de Log

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| **DEBUG** | Información detallada (solo archivo) | Request payloads, datos internos |
| **INFO** | Operaciones normales | ✅ Customer retrieved, 🔍 Getting data |
| **WARNING** | Advertencias | ⚠️ Customer not found but retrying |
| **ERROR** | Errores recuperables | ❌ Database connection failed |
| **CRITICAL** | Errores críticos | 🔥 System failure |

---

## 🧪 Ejemplo de Logs

### Console (tiempo real):
```
2025-11-25 20:55:06 | INFO     | main | 🔍 Getting customer name for phone: +573124199685
2025-11-25 20:55:06 | INFO     | main | ✅ Customer name retrieved: Willian Martinez
2025-11-25 20:55:06 | INFO     | main | 🔍 Getting case details for phone: +573124199685
2025-11-25 20:55:06 | INFO     | main | ✅ Case details retrieved: $664.0, 7 days overdue
```

### app_20251125.log (incluye DEBUG):
```
2025-11-25 20:55:05 | INFO     | main | 🔍 Getting customer name for phone: +573124199685
2025-11-25 20:55:05 | DEBUG    | main | Request payload: {'phone': '+573124199685'}
2025-11-25 20:55:06 | INFO     | httpx | HTTP Request: GET https://...supabase.co...
2025-11-25 20:55:06 | INFO     | main | ✅ Customer name retrieved: Willian Martinez
```

### errors_20251125.log (solo errores):
```
2025-11-25 21:10:32 | ERROR    | main | ❌ Error retrieving customer: Customer not found
2025-11-25 21:15:45 | CRITICAL | main | 🔥 Database connection lost
```

---

## 🔍 Cómo Monitorear Logs

### Ver logs en tiempo real:
```bash
# En consola (servidor corriendo)
uvicorn main:app --reload

# Archivo general
tail -f logs/app_20251125.log

# Solo errores
tail -f logs/errors_20251125.log
```

### Buscar en logs:
```bash
# Buscar por teléfono
grep "+573124199685" logs/app_20251125.log

# Buscar errores
grep "ERROR" logs/app_20251125.log

# Buscar llamadas a endpoints
grep "Getting customer" logs/app_20251125.log
```

### Análisis de errores:
```bash
# Ver todos los errores del día
cat logs/errors_20251125.log

# Contar errores
wc -l logs/errors_20251125.log
```

---

## 🛠️ Configuración Técnica

### Implementación (main.py):

```python
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Crear directorio si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Formato de logs
    log_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler 1: Console (INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Handler 2: File general (INFO + DEBUG)
    file_handler = RotatingFileHandler(
        filename=f"logs/app_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    
    # Handler 3: File errores (ERROR)
    error_handler = RotatingFileHandler(
        filename=f"logs/errors_{datetime.now().strftime('%Y%m%d')}.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
```

---

## 📋 Logs por Endpoint

### `/tools/get-customer-name`
```
INFO  | 🔍 Getting customer name for phone: +573124199685
DEBUG | Request payload: {'phone': '+573124199685'}
INFO  | ✅ Customer name retrieved: Willian Martinez
```

### `/tools/get-case-details`
```
INFO  | 🔍 Getting case details for phone: +573124199685
INFO  | ✅ Case details retrieved for Willian Martinez: $664.0, 7 days overdue
```

### `/tools/propose-payment-plan`
```
INFO  | 💰 Proposing payment plan for phone: +573124199685
INFO  | ✅ Installment plan: 3 payments of $221.33
```

### `/tools/update-status`
```
INFO  | 📝 Updating status for +573124199685 to 'promised_to_pay'
INFO  | ✅ Status updated successfully
INFO  | 📋 Call summary: Customer agreed to pay in 3 installments
```

---

## 🚫 Excluido de Git

Los logs están excluidos en `.gitignore`:
```
logs/
*.log
```

---

## 🎯 Buenas Prácticas

1. **Revisar logs diariamente** para detectar problemas
2. **Limpiar logs antiguos** (automático con rotation)
3. **Monitorear `errors_*.log`** para detectar issues
4. **Usar grep** para buscar patrones específicos
5. **Backup de logs importantes** antes de rotation

---

## 📈 Próximos Pasos

- [ ] Integrar con servicio de monitoreo (ej: Datadog, Sentry)
- [ ] Agregar alertas por email en errores críticos
- [ ] Dashboard para visualizar logs
- [ ] Exportar logs a formato JSON para análisis

---

**Nota**: Sistema inspirado en Serilog (.NET) con múltiples sinks y niveles configurables.

