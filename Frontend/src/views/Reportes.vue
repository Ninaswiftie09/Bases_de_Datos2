<template>
  <div class="pizzeria reportes-page">
    <div class="pizza-encabezado">
      Reportes
    </div>

    <div class="reportes-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>

      <button class="boton-recargar" @click="cargarReportes">
        Recargar
      </button>
    </div>

    <div v-if="cargando" class="estado-reportes">
      Cargando reportes...
    </div>

    <div v-else-if="error" class="estado-reportes error">
      {{ error }}
    </div>

    <div v-else class="reportes-contenido">
      <section class="reporte-seccion">
        <h2>Top restaurantes</h2>

        <div v-if="topRestaurantes.length === 0" class="estado-vacio">
          No hay datos disponibles.
        </div>

        <div v-else class="pizza-grid">
          <div
            v-for="item in topRestaurantes"
            :key="item._id"
            class="pizza-card pizza-vegetal"
          >
            <h3>{{ obtenerNombreRestaurante(item) }}</h3>

            <p class="reporte-dato">
              <strong>Rating promedio:</strong>
              {{ formatearNumero(item.avgRating) }}
            </p>

            <p class="reporte-dato">
              <strong>Total de reseñas:</strong>
              {{ item.totalReviews || 0 }}
            </p>
          </div>
        </div>
      </section>

      <section class="reporte-seccion">
        <h2>Top platillos</h2>

        <div v-if="topPlatillos.length === 0" class="estado-vacio">
          No hay datos disponibles.
        </div>

        <div v-else class="pizza-grid">
          <div
            v-for="item in topPlatillos"
            :key="item._id"
            class="pizza-card pizza-clasico"
          >
            <h3>{{ obtenerNombrePlatillo(item) }}</h3>

            <p class="reporte-dato">
              <strong>Total vendido:</strong>
              {{ item.totalSold || 0 }}
            </p>
          </div>
        </div>
      </section>

      <section class="reporte-seccion">
        <h2>Órdenes por estado</h2>

        <div v-if="ordenesPorEstado.length === 0" class="estado-vacio">
          No hay datos disponibles.
        </div>

        <div v-else class="estado-grid">
          <div
            v-for="item in ordenesPorEstado"
            :key="item._id"
            class="estado-card"
            :class="obtenerClaseEstado(item._id)"
          >
            <p class="estado-nombre">
              {{ capitalizarEstado(item._id) }}
            </p>
            <p class="estado-total">
              {{ item.total }}
            </p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const topRestaurantes = ref([])
const topPlatillos = ref([])
const ordenesPorEstado = ref([])
const cargando = ref(true)
const error = ref('')

const baseURL = 'http://localhost:8000/api/reports'

const cargarReportes = async () => {
  cargando.value = true
  error.value = ''

  try {
    const [restaurantesRes, platillosRes, estadosRes] = await Promise.all([
      fetch(`${baseURL}/top-restaurants`),
      fetch(`${baseURL}/top-dishes`),
      fetch(`${baseURL}/orders-by-status`)
    ])

    if (!restaurantesRes.ok || !platillosRes.ok || !estadosRes.ok) {
      throw new Error('No se pudieron cargar todos los reportes')
    }

    const restaurantesData = await restaurantesRes.json()
    const platillosData = await platillosRes.json()
    const estadosData = await estadosRes.json()

    console.log('Top restaurantes:', restaurantesData)
    console.log('Top platillos:', platillosData)
    console.log('Órdenes por estado:', estadosData)

    topRestaurantes.value = Array.isArray(restaurantesData) ? restaurantesData : []
    topPlatillos.value = Array.isArray(platillosData) ? platillosData : []
    ordenesPorEstado.value = Array.isArray(estadosData) ? estadosData : []
  } catch (err) {
    console.error('Error al cargar reportes:', err)
    error.value = 'No se pudieron cargar los reportes desde el backend.'
  } finally {
    cargando.value = false
  }
}

const obtenerNombreRestaurante = (item) => {
  if (item?.restaurant?.[0]?.name) return item.restaurant[0].name
  return item?._id || 'Restaurante sin nombre'
}

const obtenerNombrePlatillo = (item) => {
  if (item?.dish?.[0]?.name) return item.dish[0].name
  return item?._id || 'Platillo sin nombre'
}

const formatearNumero = (valor) => {
  const numero = Number(valor)
  if (Number.isNaN(numero)) return '0.0'
  return numero.toFixed(1)
}

const capitalizarEstado = (estado) => {
  if (!estado) return 'Sin estado'
  return estado.charAt(0).toUpperCase() + estado.slice(1)
}

const obtenerClaseEstado = (estado) => {
  switch (estado) {
    case 'pending':
      return 'estado-pending'
    case 'confirmed':
      return 'estado-confirmed'
    case 'preparing':
      return 'estado-preparing'
    case 'delivered':
      return 'estado-delivered'
    case 'cancelled':
      return 'estado-cancelled'
    default:
      return 'estado-default'
  }
}

onMounted(() => {
  cargarReportes()
})
</script>

<style scoped>
.reportes-page {
  padding-bottom: 1rem;
}

.reportes-barra {
  padding: 1rem 1.2rem 0;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.boton-secundario,
.boton-recargar {
  display: inline-block;
  text-decoration: none;
  border: 0;
  background: var(--albahaca);
  color: white;
  padding: 0.55rem 1rem;
  border-radius: 999px;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.12);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.boton-recargar {
  background: var(--pepperoni);
}

.boton-secundario:hover,
.boton-recargar:hover {
  transform: translateY(-2px);
  box-shadow: 0 9px 16px rgba(0, 0, 0, 0.18);
}

.estado-reportes {
  padding: 2rem 1.2rem;
  text-align: center;
  font-size: 1.05rem;
}

.error {
  color: var(--salsa);
  font-weight: 700;
}

.reportes-contenido {
  padding: 1rem 1.2rem 1.2rem;
}

.reporte-seccion + .reporte-seccion {
  margin-top: 2rem;
}

.reporte-seccion h2 {
  margin: 0 0 1rem;
  color: var(--salsa);
}

.reporte-dato {
  margin: 0.45rem 0;
  line-height: 1.45;
}

.estado-vacio {
  color: #6b5a45;
}

.estado-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
}

.estado-card {
  border-radius: 14px;
  padding: 1.1rem;
  color: white;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.12);
}

.estado-nombre {
  margin: 0 0 0.4rem;
  font-weight: 700;
}

.estado-total {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 900;
}

.estado-pending {
  background: linear-gradient(135deg, #d99a00, #b67d00);
}

.estado-confirmed {
  background: linear-gradient(135deg, #3b7d3f, #2d6531);
}

.estado-preparing {
  background: linear-gradient(135deg, #d93a2e, #b52f24);
}

.estado-delivered {
  background: linear-gradient(135deg, #2f8f5b, #246f47);
}

.estado-cancelled {
  background: linear-gradient(135deg, #7d2a2a, #5f1f1f);
}

.estado-default {
  background: linear-gradient(135deg, #8d6e63, #6d4c41);
}
</style>