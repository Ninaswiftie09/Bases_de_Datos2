import { createRouter, createWebHistory } from 'vue-router'

// Vistas
import Home from '../views/Home.vue'
import Menu from '../views/Menu.vue'
import Ordenes from '../views/Ordenes.vue'
import Reportes from '../views/Reportes.vue'
import Restaurantes from '../views/Restaurantes.vue'
import Usuarios from '../views/Usuarios.vue'

const routes = [
  { path: '/', redirect: '/home' },

  { path: '/home', name: 'home', component: Home },
  { path: '/menu', name: 'menu', component: Menu },
  { path: '/ordenes', name: 'ordenes', component: Ordenes },
  { path: '/reportes', name: 'reportes', component: Reportes },
  { path: '/restaurantes', name: 'restaurantes', component: Restaurantes },
  { path: '/usuarios', name: 'usuarios', component: Usuarios },

  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: {
      template: `
        <div style="text-align:center; padding: 2rem;">
          <h1>404 - Página no encontrada</h1>
          <p>La ruta ingresada no existe.</p>
          <router-link to="/home">Volver al inicio</router-link>
        </div>
      `
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router