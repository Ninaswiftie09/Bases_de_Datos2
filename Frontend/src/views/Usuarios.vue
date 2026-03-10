<template>
  <div class="pizzeria">
    <div class="pizza-encabezado">
      Usuarios de Tridata
    </div>

    <div class="usuarios-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="cargando" class="estado-usuarios">
      Cargando usuarios...
    </div>

    <div v-else-if="error" class="estado-usuarios error">
      {{ error }}
    </div>

    <div v-else-if="usuarios.length === 0" class="estado-usuarios">
      No hay usuarios registrados.
    </div>

    <div v-else class="pizza-grid">
      <div
        v-for="usuario in usuarios"
        :key="usuario._id"
        class="pizza-card usuario-card"
      >
        <h3>{{ nombreCompleto(usuario) }}</h3>

        <p class="usuario-dato">
          <strong>Correo:</strong> {{ usuario.email }}
        </p>

        <p class="usuario-dato">
          <strong>Teléfono:</strong> {{ usuario.phone }}
        </p>

        <div class="usuario-direcciones">
          <p class="usuario-subtitulo">Direcciones:</p>

          <div
            v-if="usuario.addresses && usuario.addresses.length > 0"
            class="direcciones-lista"
          >
            <div
              v-for="(direccion, index) in usuario.addresses"
              :key="index"
              class="direccion-item"
            >
              <p><strong>{{ direccion.label || 'Dirección' }}</strong></p>
              <p>{{ direccion.street }}</p>
              <p>{{ direccion.city }}</p>
              <p v-if="direccion.zone">Zona: {{ direccion.zone }}</p>
              <p v-if="direccion.reference">Referencia: {{ direccion.reference }}</p>
            </div>
          </div>

          <p v-else class="sin-direcciones">
            Este usuario no tiene direcciones registradas.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const usuarios = ref([])
const cargando = ref(true)
const error = ref('')

const endpoint = 'http://localhost:8000/api/users'

const cargarUsuarios = async () => {
  cargando.value = true
  error.value = ''

  try {
    const response = await fetch(endpoint)
    console.log('Status usuarios:', response.status)

    if (!response.ok) {
      throw new Error(`Error ${response.status}`)
    }

    const data = await response.json()
    console.log('Respuesta usuarios:', data)

    if (Array.isArray(data)) {
      usuarios.value = data
    } else if (Array.isArray(data.data)) {
      usuarios.value = data.data
    } else if (Array.isArray(data.results)) {
      usuarios.value = data.results
    } else if (Array.isArray(data.items)) {
      usuarios.value = data.items
    } else {
      console.warn('Formato no reconocido en usuarios:', data)
      usuarios.value = []
    }

    console.log('Usuarios finales:', usuarios.value)
  } catch (err) {
    console.error('Error al cargar usuarios:', err)
    error.value = 'No se pudieron cargar los usuarios desde el backend.'
  } finally {
    cargando.value = false
  }
}

const nombreCompleto = (usuario) => {
  const first = usuario?.name?.first || ''
  const last = usuario?.name?.last || ''
  return `${first} ${last}`.trim() || 'Usuario sin nombre'
}

onMounted(() => {
  cargarUsuarios()
})
</script>

<style scoped>
.usuarios-barra {
  padding: 1rem 1.2rem 0;
}

.boton-secundario {
  display: inline-block;
  text-decoration: none;
  background: var(--albahaca);
  color: white;
  padding: 0.55rem 1rem;
  border-radius: 999px;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.boton-secundario:hover {
  transform: translateY(-2px);
  box-shadow: 0 9px 16px rgba(0, 0, 0, 0.18);
}

.estado-usuarios {
  padding: 2rem 1.2rem;
  text-align: center;
  font-size: 1.05rem;
}

.error {
  color: var(--salsa);
  font-weight: 700;
}

.usuario-card {
  border-left: 5px solid var(--albahaca);
  background: #fffaf0;
}

.usuario-dato {
  margin: 0.45rem 0;
  line-height: 1.45;
}

.usuario-subtitulo {
  margin: 1rem 0 0.6rem;
  font-weight: 800;
  color: var(--salsa);
}

.direcciones-lista {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.direccion-item {
  background: #fff3da;
  border: 1px solid #f2c572;
  border-radius: 10px;
  padding: 0.8rem;
}

.direccion-item p {
  margin: 0.2rem 0;
}

.sin-direcciones {
  margin: 0.4rem 0 0;
  color: #6b5a45;
}
</style>