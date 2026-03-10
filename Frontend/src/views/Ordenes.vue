<template>
  <div class="pizzeria">
    <div class="pizza-encabezado">
      Órdenes
    </div>

    <div class="ordenes-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="cargando" class="estado-ordenes">
      Cargando órdenes...
    </div>

    <div v-else-if="error" class="estado-ordenes error">
      {{ error }}
    </div>

    <div v-else-if="ordenes.length === 0" class="estado-ordenes">
      No hay órdenes registradas.
    </div>

    <div v-else class="pizza-grid">
      <div
        v-for="orden in ordenes"
        :key="orden._id"
        class="pizza-card orden-card"
        :class="obtenerClaseEstado(orden.status)"
      >
        <div class="orden-header">
          <h3>Orden #{{ orden._id?.slice(-6) || '---' }}</h3>
          <span class="estado-badge" :class="obtenerBadgeEstado(orden.status)">
            {{ capitalizarEstado(orden.status) }}
          </span>
        </div>

        <p class="orden-meta">
          <strong>Usuario:</strong> {{ mostrarReferencia(orden.user_id) }}
        </p>

        <p class="orden-meta">
          <strong>Restaurante:</strong> {{ mostrarReferencia(orden.restaurant_id) }}
        </p>

        <p class="orden-meta">
          <strong>Fecha:</strong> {{ formatearFecha(orden.created_at) }}
        </p>

        <div class="orden-totales">
          <div>
            <span class="total-label">Subtotal</span>
            <span class="total-valor">Q{{ formatearPrecio(orden.totals?.subtotal) }}</span>
          </div>
          <div>
            <span class="total-label">Total</span>
            <span class="total-valor total-final">Q{{ formatearPrecio(orden.totals?.total) }}</span>
          </div>
        </div>

        <div class="orden-items">
          <p class="items-titulo">
            Productos ({{ orden.items?.length || 0 }})
          </p>

          <div v-if="orden.items && orden.items.length > 0" class="items-lista">
            <div
              v-for="(item, index) in orden.items"
              :key="index"
              class="item-card"
            >
              <div class="item-top">
                <span class="item-nombre">{{ item.name_snapshot }}</span>
                <span class="item-cantidad">x{{ item.qty }}</span>
              </div>

              <p class="item-precio">
                Q{{ formatearPrecio(item.price_snapshot) }}
              </p>

              <p v-if="item.notes" class="item-notas">
                Nota: {{ item.notes }}
              </p>
            </div>
          </div>

          <p v-else class="sin-items">
            Esta orden no tiene productos.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'

const ordenes = ref([])
const cargando = ref(true)
const error = ref('')

const endpoint = 'http://localhost:8000/api/orders'

const cargarOrdenes = async () => {
  cargando.value = true
  error.value = ''

  try {
    const response = await fetch(endpoint)
    console.log('Status órdenes:', response.status)

    if (!response.ok) {
      throw new Error(`Error ${response.status}`)
    }

    const data = await response.json()
    console.log('Respuesta órdenes:', data)

    if (Array.isArray(data)) {
      ordenes.value = data
    } else if (Array.isArray(data.data)) {
      ordenes.value = data.data
    } else if (Array.isArray(data.results)) {
      ordenes.value = data.results
    } else if (Array.isArray(data.items)) {
      ordenes.value = data.items
    } else {
      console.warn('Formato no reconocido en órdenes:', data)
      ordenes.value = []
    }

    console.log('Órdenes finales:', ordenes.value)
  } catch (err) {
    console.error('Error al cargar órdenes:', err)
    error.value = 'No se pudieron cargar las órdenes desde el backend.'
  } finally {
    cargando.value = false
  }
}

const formatearPrecio = (precio) => {
  const numero = Number(precio)
  if (Number.isNaN(numero)) return '0.00'
  return numero.toFixed(2)
}

const formatearFecha = (fecha) => {
  if (!fecha) return 'Sin fecha'
  return new Date(fecha).toLocaleString('es-GT')
}

const capitalizarEstado = (estado) => {
  if (!estado) return 'Sin estado'
  return estado.charAt(0).toUpperCase() + estado.slice(1)
}

const mostrarReferencia = (valor) => {
  if (!valor) return 'No disponible'
  if (typeof valor === 'object') {
    return valor.name || valor.email || valor._id || 'Objeto relacionado'
  }
  return valor
}

const obtenerClaseEstado = (estado) => {
  switch (estado) {
    case 'pending':
      return 'pizza-queso'
    case 'confirmed':
      return 'pizza-vegetal'
    case 'preparing':
      return 'pizza-clasico'
    case 'delivered':
      return 'pizza-vegetal'
    case 'cancelled':
      return 'pizza-clasico'
    default:
      return 'pizza-queso'
  }
}

const obtenerBadgeEstado = (estado) => {
  switch (estado) {
    case 'pending':
      return 'badge-pending'
    case 'confirmed':
      return 'badge-confirmed'
    case 'preparing':
      return 'badge-preparing'
    case 'delivered':
      return 'badge-delivered'
    case 'cancelled':
      return 'badge-cancelled'
    default:
      return 'badge-pending'
  }
}

onMounted(() => {
  cargarOrdenes()
})
</script>

<style scoped>
.ordenes-barra {
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

.estado-ordenes {
  padding: 2rem 1.2rem;
  text-align: center;
  font-size: 1.05rem;
}

.error {
  color: var(--salsa);
  font-weight: 700;
}

.orden-card {
  background: #fffaf0;
}

.orden-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 0.8rem;
}

.orden-header h3 {
  margin: 0;
}

.estado-badge {
  display: inline-block;
  padding: 0.28rem 0.65rem;
  border-radius: 999px;
  color: white;
  font-size: 0.82rem;
  font-weight: 800;
}

.badge-pending {
  background: #d99a00;
}

.badge-confirmed {
  background: #3b7d3f;
}

.badge-preparing {
  background: #d93a2e;
}

.badge-delivered {
  background: #2f8f5b;
}

.badge-cancelled {
  background: #7d2a2a;
}

.orden-meta {
  margin: 0.35rem 0;
  line-height: 1.45;
  word-break: break-word;
}

.orden-totales {
  margin: 1rem 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.orden-totales > div {
  background: #fff3da;
  border: 1px solid #f2c572;
  border-radius: 10px;
  padding: 0.75rem;
}

.total-label {
  display: block;
  font-size: 0.9rem;
  color: #6b5a45;
  margin-bottom: 0.2rem;
}

.total-valor {
  display: block;
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--texto);
}

.total-final {
  color: var(--salsa);
}

.orden-items {
  margin-top: 0.9rem;
}

.items-titulo {
  margin: 0 0 0.7rem;
  font-weight: 800;
  color: var(--salsa);
}

.items-lista {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}

.item-card {
  background: #fff8e3;
  border: 1px solid #f2c572;
  border-radius: 10px;
  padding: 0.75rem;
}

.item-top {
  display: flex;
  justify-content: space-between;
  gap: 0.6rem;
}

.item-nombre {
  font-weight: 700;
}

.item-cantidad {
  font-weight: 800;
  color: var(--salsa);
}

.item-precio {
  margin: 0.35rem 0 0;
  font-weight: 700;
}

.item-notas {
  margin: 0.35rem 0 0;
  font-size: 0.92rem;
  color: #6b5a45;
}

.sin-items {
  margin: 0;
  color: #6b5a45;
}
</style>