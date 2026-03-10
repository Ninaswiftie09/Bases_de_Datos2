<template>
  <div class="pizzeria">
    <div class="pizza-encabezado">
      Menú de TriData
    </div>

    <div class="menu-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="cargando" class="estado-menu">
      Cargando productos...
    </div>

    <div v-else-if="error" class="estado-menu error">
      {{ error }}
    </div>

    <div v-else-if="productos.length === 0" class="estado-menu">
      No hay productos en el menú.
    </div>

    <div v-else class="pizza-grid">
      <div
        v-for="producto in productos"
        :key="producto._id"
        class="pizza-card"
        :class="producto.is_available ? 'pizza-queso' : 'pizza-clasico'"
      >
        <h3>{{ producto.name }}</h3>

        <p class="pizza-descripcion">
          {{ producto.description }}
        </p>

        <p class="pizza-precio">
          Q{{ formatearPrecio(producto.price) }}
        </p>

        <p
          class="pizza-estado"
          :class="producto.is_available ? 'disponible' : 'nodisponible'"
        >
          {{ producto.is_available ? 'Disponible' : 'No disponible' }}
        </p>

        <p class="pizza-restaurante">
          Restaurante: {{ obtenerNombreRestaurante(producto.restaurant_id) }}
        </p>

        <button class="boton-orden" :disabled="!producto.is_available">
          Ordenar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const productos = ref([])
const cargando = ref(true)
const error = ref('')

// Usar URL completa para probar directo contra backend
const endpoint = 'http://localhost:8000/api/menu-items'

const cargarMenu = async () => {
  cargando.value = true
  error.value = ''

  try {
    const response = await fetch(endpoint)
    console.log('Status:', response.status)

    if (!response.ok) {
      throw new Error(`Error ${response.status}`)
    }

    const data = await response.json()
    console.log('Respuesta backend:', data)

    if (Array.isArray(data)) {
      productos.value = data
    } else if (Array.isArray(data.data)) {
      productos.value = data.data
    } else if (Array.isArray(data.results)) {
      productos.value = data.results
    } else if (Array.isArray(data.items)) {
      productos.value = data.items
    } else {
      console.warn('Formato no reconocido:', data)
      productos.value = []
    }

    console.log('Productos finales:', productos.value)
  } catch (err) {
    console.error('Error al cargar menú:', err)
    error.value = 'No se pudo cargar el menú desde el backend.'
  } finally {
    cargando.value = false
  }
}

const formatearPrecio = (precio) => {
  const numero = Number(precio)
  if (Number.isNaN(numero)) return '0.00'
  return numero.toFixed(2)
}

const obtenerNombreRestaurante = (restaurantId) => {
  if (!restaurantId) return 'Sin restaurante'

  if (typeof restaurantId === 'object') {
    return restaurantId.name || restaurantId._id || 'Restaurante sin nombre'
  }

  return restaurantId
}

onMounted(() => {
  cargarMenu()
})
</script>

<style scoped>
.menu-barra {
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

.estado-menu {
  padding: 2rem 1.2rem;
  text-align: center;
  font-size: 1.05rem;
}

.error {
  color: var(--salsa);
  font-weight: 700;
}

.pizza-descripcion {
  margin: 0.7rem 0;
  line-height: 1.5;
  min-height: 48px;
}

.pizza-precio {
  font-size: 1.15rem;
  font-weight: 800;
  color: var(--salsa);
  margin: 0.7rem 0 0.35rem;
}

.pizza-estado {
  margin: 0 0 0.6rem;
  font-weight: 700;
}

.disponible {
  color: var(--albahaca);
}

.nodisponible {
  color: var(--pepperoni);
}

.pizza-restaurante {
  font-size: 0.9rem;
  color: #6b5a45;
  margin-bottom: 0.8rem;
  word-break: break-word;
}

.boton-orden:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>