<template>
  <section class="home" :style="{ '--bg-image': `url(${fondo})` }">
    <div class="home__background"></div>
    <div class="home__overlay"></div>

    <div class="home__content">
      <div class="home__hero">
        <h1>Panel de Restaurante TriData</h1>
        <p>
          Bienvenido al sistema. Seleccione la sección que desea administrar.
        </p>
      </div>

      <div class="home__options">
        <RouterLink to="/menu" class="home__card">
          <h2>Menú</h2>
          <p>Ver y administrar las pizzas, ingredientes y productos.</p>
        </RouterLink>

        <RouterLink to="/ordenes" class="home__card">
          <h2>Órdenes</h2>
          <p>Revisar pedidos, estados y seguimiento de órdenes.</p>
        </RouterLink>

        <RouterLink to="/reportes" class="home__card">
          <h2>Reportes</h2>
          <p>Consultar ventas, estadísticas y resúmenes del negocio.</p>
        </RouterLink>

        <RouterLink to="/restaurantes" class="home__card">
          <h2>Restaurantes</h2>
          <p>Administrar sucursales, ubicaciones y datos generales.</p>
        </RouterLink>

        <RouterLink to="/usuarios" class="home__card">
          <h2>Usuarios</h2>
          <p>Gestionar cuentas, roles y permisos del sistema.</p>
        </RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import fondo from '../assets/fondohome.jpg'
</script>

<style scoped>
.home {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.home__background {
  position: absolute;
  inset: 0;
  background-image: var(--bg-image);
  background-size: cover;
  background-position: center;
  filter: blur(5px);
  transform: scale(1.06);
  z-index: 0;
}

.home__overlay {
  position: absolute;
  inset: 0;
  background: rgba(58, 45, 32, 0.30);
  z-index: 1;
}

.home__content {
  position: relative;
  z-index: 2;
  width: min(1100px, 92%);
  padding: 2rem 1rem;
}

.home__hero {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

.home__hero h1 {
  margin: 0 0 0.75rem;
  font-size: clamp(2rem, 4vw, 3.2rem);
  font-weight: 900;
  text-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}

.home__hero p {
  margin: 0 auto;
  max-width: 650px;
  font-size: 1.05rem;
  line-height: 1.6;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.25);
}

.home__options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.2rem;
}

.home__card {
  text-decoration: none;
  color: var(--texto);
  background: rgba(255, 250, 240, 0.92);
  border: 2px solid #fbce8f;
  border-radius: 18px;
  padding: 1.3rem;
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.16);
  backdrop-filter: blur(2px);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.home__card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.22);
}

.home__card h2 {
  margin-top: 0;
  margin-bottom: 0.55rem;
  color: var(--salsa);
  font-size: 1.25rem;
}

.home__card p {
  margin: 0;
  line-height: 1.5;
}
</style>