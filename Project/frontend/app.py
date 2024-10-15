import streamlit as st
import requests
from datetime import datetime

API_URL = "http://localhost:8000"  # Cambia esto si es necesario

# Imagen centrada
st.markdown('<div style="text-align: center;">'
            '<img src="https://www.zarla.com/images/zarla-mi-lugar-feliz-1x1-2400x2400-20210603-6wr8prhhtcx3wbmyvgp8.png?crop=1:1,smart&width=250&dpr=2" width="200">'
            '</div>', unsafe_allow_html=True)

# Títulos y descripciones más llamativas con markdown
st.markdown("<h1 style='text-align: center; color: #FF5733;'>LinkScribe</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4C4B4B;'>Organiza y gestiona tus enlaces de manera eficiente</p>", unsafe_allow_html=True)

# Menú en la barra lateral con título estilizado
st.sidebar.title("Navegación")
menu = ["Registro", "Inicio de Sesión"]
choice = st.sidebar.radio("Selecciona una opción", menu)

# Funciones de registro e inicio de sesión
def register_user(username, password):
    try:
        response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
        response.raise_for_status()  # Lanza un error si la respuesta no es 200
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Error HTTP: {http_err}")
    except Exception as err:
        st.error(f"Ocurrió un error: {err}")
    return None

def login_user(username, password):
    try:
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        st.error(f"Error HTTP: {http_err}")
    except Exception as err:
        st.error(f"Ocurrió un error: {err}")
    return None

# Página de registro con estilos
if choice == "Registro":
    st.subheader("Registro de Usuario")
    st.markdown("<p style='color: #FF5733;'>Crea tu cuenta para empezar a organizar tus enlaces.</p>", unsafe_allow_html=True)
    
    username = st.text_input("Nombre de usuario", placeholder="Introduce un nombre de usuario")
    password = st.text_input("Contraseña", type='password', placeholder="Introduce una contraseña segura")
    
    if st.button("Registrar"):
        result = register_user(username, password)
        if result and "msg" in result:
            st.success(result["msg"])
        else:
            st.error("No se pudo completar el registro. Intenta nuevamente.")

# Página de inicio de sesión con estilos
elif choice == "Inicio de Sesión":
    st.subheader("Inicio de Sesión")
    st.markdown("<p style='color: #FF5733;'>Ingresa tus credenciales para acceder a tu cuenta.</p>", unsafe_allow_html=True)
    
    username = st.text_input("Nombre de usuario", placeholder="Introduce tu nombre de usuario")
    password = st.text_input("Contraseña", type='password', placeholder="Introduce tu contraseña")
    
    if st.button("Iniciar Sesión"):
        result = login_user(username, password)
        if result and "access_token" in result:
            st.session_state['token'] = result['access_token']
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.success(f"¡Bienvenid@, {username}!")
            st.rerun()  # Cambiado aquí
        else:
            st.error("Las credenciales no son correctas. Inténtalo de nuevo.")

# Si el usuario está autenticado
if 'logged_in' in st.session_state and st.session_state['logged_in']:
    st.success(f"¡Bienvenid@ de nuevo, {st.session_state['username']}!")

    # Expansor para mostrar los enlaces
    with st.expander("Tus Enlaces Guardados", expanded=True):  # Cambiado aquí
        st.subheader("Lista de Enlaces")
        response = requests.get(f"{API_URL}/links", headers={"Authorization": f"Bearer {st.session_state['token']}"})

        # Búsqueda de enlaces
        search_term = st.text_input("Buscar enlaces por descripción o título", "")
        if search_term:
            response = requests.get(f"{API_URL}/links?search={search_term}", headers={"Authorization": f"Bearer {st.session_state['token']}"})
        else:
            response = requests.get(f"{API_URL}/links", headers={"Authorization": f"Bearer {st.session_state['token']}"})

        if response.status_code == 200:
            links = response.json()
            if links:
                for link in links:
                    st.write(f"**ID:** {link['id']}")
                    st.write(f"**URL:** [{link['url']}]({link['url']})")
                    st.write(f"**Descripción:** {link['descripcion']}")
                    st.write(f"**Categoría:** {link.get('categoria', 'Sin categoría')}")
                    st.write(f"**Creado el:** {datetime.fromisoformat(link['created_at']).date()}")
                    st.write("---")
            else:
                st.write("No se encontraron enlaces.")
        else:
            st.error("Error al obtener los enlaces.")

    # Expansor para agregar enlaces
    with st.expander("Agregar Nuevo Enlace", expanded=False):  # Cambiado aquí
        st.subheader("Agregar Enlace")

        # Inputs estilizados
        url = st.text_input("URL del enlace", placeholder="Introduce la URL del enlace")
        descripcion = st.text_input("Descripción", placeholder="Describe brevemente el enlace")

        if st.button("Agregar Enlace"):
            if url and descripcion:
                response = requests.post(f"{API_URL}/links", json={
                    "url": url,
                    "descripcion": descripcion
                }, headers={"Authorization": f"Bearer {st.session_state['token']}"})

                if response.status_code == 200:
                    st.success("¡Enlace agregado con éxito!")
                    st.rerun()  # Cambiado aquí
                else:
                    st.error("Error al agregar el enlace.")
            else:
                st.error("Por favor completa todos los campos.")
