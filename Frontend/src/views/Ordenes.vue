<template>
  <div class="pizzeria">
    <div class="pizza-encabezado">
      Órdenes
    </div>

    <div class="menu-barra">
      <router-link to="/home" class="boton-secundario">
        ← Volver al inicio
      </router-link>
    </div>

    <div v-if="cargando" class="estado-menu">
      Cargando órdenes...
    </div>

    <div v-else-if="error" class="estado-menu error">
      {{ error }}
    </div>

    <div v-else-if="ordenes.length === 0" class="estado-menu">
      No hay órdenes registradas.
    </div>

    <div v-else class="pizza-grid">
      <div
        v-for="orden in ordenes"
        :key="orden._id"
        class="pizza-card pizza-queso"
      >
        <h3>Orden #{{ orden._id.slice(-6) }}</h3>

        <p class="pizza-descripcion">
          Estado: {{ orden.status }}
        </p>

        <p class="pizza-precio">
          Total: Q{{ formatearPrecio(orden.totals.total) }}
        </p>

        <p class="pizza-restaurante">
          Usuario: {{ mostrarReferencia(orden.user_id) }}
        </p>

        <p class="pizza-restaurante">
          Restaurante: {{ mostrarReferencia(orden.restaurant_id) }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const ordenes = ref([]);
const cargando = ref(true);
const error = ref("");

const cargarOrdenes = async () => {
  try {
    const response = await fetch("http://localhost:8000/api/orders");
    const data = await response.json();
    ordenes.value = data.data;
  } catch (err) {
    error.value = "No se pudieron cargar las órdenes.";
  } finally {
    cargando.value = false;
  }
};

const formatearPrecio = (precio) => {
  const numero = Number(precio);
  if (Number.isNaN(numero)) return "0.00";
  return numero.toFixed(2);
};

const mostrarReferencia = (valor) => {
  if (!valor) return "No disponible";
  if (typeof valor === "object") {
    return valor.name || valor.email || valor._id;
  }
  return valor;
};

onMounted(() => {
  cargarOrdenes();
});
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
</style>