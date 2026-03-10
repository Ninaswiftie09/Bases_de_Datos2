<template>
  <div class="pizzeria">
    <div class="pizza-encabezado">
      Restaurantes
    </div>

    <div class="restaurantes-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="cargando" class="estado-restaurantes">
      Cargando restaurantes...
    </div>

    <div v-else-if="error" class="estado-restaurantes error">
      {{ error }}
    </div>

    <div v-else-if="restaurantes.length === 0" class="estado-restaurantes">
      No hay restaurantes registrados.
    </div>

    <div v-else class="pizza-grid">
      <div
        v-for="restaurante in restaurantes"
        :key="restaurante._id"
        class="pizza-card restaurante-card"
        :class="obtenerClaseCategoria(restaurante.category)"
      >
        <h3>{{ restaurante.name }}</h3>

        <p class="restaurante-categoria">
          {{ restaurante.category }}
        </p>

        <p class="restaurante-direccion">
          {{ restaurante.location?.address || 'Sin dirección registrada' }}
        </p>

        <div class="restaurante-rating">
          <span class="rating-valor">
            ⭐ {{ formatearRating(restaurante.avg_rating) }}
          </span>
          <span class="rating-resenas">
            {{ restaurante.review_count || 0 }} reseñas
          </span>
        </div>

        <p class="restaurante-coordenadas">
          Coordenadas:
          {{ obtenerCoordenadas(restaurante.location?.geo?.coordinates) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const restaurantes = ref([])
const cargando = ref(true)
const error = ref('')

const endpoint = 'http://localhost:8000/api/restaurants'

const cargarRestaurantes = async () => {
  cargando.value = true
  error.value = ''

  try {
    const response = await fetch(endpoint)
    console.log('Status restaurantes:', response.status)

    if (!response.ok) {
      throw new Error(`Error ${response.status}`)
    }

    const data = await response.json()
    console.log('Respuesta restaurantes:', data)

    if (Array.isArray(data)) {
      restaurantes.value = data
    } else if (Array.isArray(data.data)) {
      restaurantes.value = data.data
    } else if (Array.isArray(data.results)) {
      restaurantes.value = data.results
    } else if (Array.isArray(data.items)) {
      restaurantes.value = data.items
    } else {
      console.warn('Formato no reconocido en restaurantes:', data)
      restaurantes.value = []
    }

    console.log('Restaurantes finales:', restaurantes.value)
  } catch (err) {
    console.error('Error al cargar restaurantes:', err)
    error.value = 'No se pudieron cargar los restaurantes desde el backend.'
  } finally {
    cargando.value = false
  }
}

const obtenerClaseCategoria = (categoria) => {
  const cat = (categoria || '').toLowerCase()

  if (cat.includes('pizza') || cat.includes('ital')) return 'pizza-clasico'
  if (cat.includes('fast') || cat.includes('comida')) return 'pizza-queso'
  if (cat.includes('veg') || cat.includes('salud')) return 'pizza-vegetal'

  return 'pizza-queso'
}

const formatearRating = (rating) => {
  const numero = Number(rating)
  if (Number.isNaN(numero)) return '0.0'
  return numero.toFixed(1)
}

const obtenerCoordenadas = (coordinates) => {
  if (!Array.isArray(coordinates) || coordinates.length !== 2) {
    return 'No disponibles'
  }

  const [lng, lat] = coordinates
  return `${lat}, ${lng}`
}

onMounted(() => {
  cargarRestaurantes()
})
</script>

<style scoped>
.restaurantes-barra {
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

.estado-restaurantes {
  padding: 2rem 1.2rem;
  text-align: center;
  font-size: 1.05rem;
}

.error {
  color: var(--salsa);
  font-weight: 700;
}

.restaurante-card {
  background: #fffaf0;
}

.restaurante-categoria {
  margin: 0.45rem 0 0.6rem;
  font-weight: 700;
  color: var(--salsa);
  text-transform: capitalize;
}

.restaurante-direccion {
  margin: 0.5rem 0 0.8rem;
  line-height: 1.5;
  min-height: 48px;
}

.restaurante-rating {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin: 0.8rem 0;
  padding: 0.65rem 0.8rem;
  background: #fff3da;
  border: 1px solid #f2c572;
  border-radius: 10px;
}

.rating-valor {
  font-weight: 800;
  color: #8a4b00;
}

.rating-resenas {
  font-size: 0.92rem;
  color: #6b5a45;
}

.restaurante-coordenadas {
  margin: 0.7rem 0 0;
  font-size: 0.9rem;
  color: #6b5a45;
  word-break: break-word;
}
</style>