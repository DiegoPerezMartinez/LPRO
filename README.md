## Instalación de entorno y Flet

### Requisitos previos
- Tener instalado **Python**

### Pasos para la instalación

1. Crear un entorno virtual:

```bash
python -m venv .venv
```

2. Activar el entorno virtual:

- En **Windows**:

```bash
.venv\Scripts\activate
```

- En **Linux/MacOS**:

```bash
source .venv/bin/activate
```

3. Instalar Flet con todas sus dependencias:

```bash
pip install flet[all]
```

4. Verificar la versión de Flet instalada:

```bash
flet --version
```

5. Ejecutar una aplicación Flet:

```bash
flet run
```

