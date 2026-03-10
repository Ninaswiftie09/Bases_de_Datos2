<template>
  <div class="container">
    <h1>Proyecto 01 - MongoDB</h1>
    <p class="subtitle">Prueba básica de conexión entre Vue, Express y MongoDB</p>

    <form class="form" @submit.prevent="createRestaurant">
      <input v-model="form.name" type="text" placeholder="Nombre del restaurante" />
      <input v-model="form.category" type="text" placeholder="Categoría" />
      <input v-model="form.address" type="text" placeholder="Dirección" />
      <input v-model.number="form.rating" type="number" min="0" max="5" step="0.1" placeholder="Rating" />
      <button type="submit">Agregar restaurante</button>
    </form>

    <button class="refresh" @click="fetchRestaurants">Actualizar lista</button>

    <p v-if="loading">Cargando...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div class="list">
      <div v-for="restaurant in restaurants" :key="restaurant._id" class="card">
        <h3>{{ restaurant.name }}</h3>
        <p><strong>Categoría:</strong> {{ restaurant.category }}</p>
        <p><strong>Dirección:</strong> {{ restaurant.address }}</p>
        <p><strong>Rating:</strong> {{ restaurant.rating }}</p>
        <button class="delete" @click="deleteRestaurant(restaurant._id)">Eliminar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

const API_URL = "http://localhost:8000/api";

const restaurants = ref([]);
const loading = ref(false);
const error = ref("");

const form = reactive({
  name: "",
  category: "",
  address: "",
  rating: 0,
});

const fetchRestaurants = async () => {
  loading.value = true;
  error.value = "";

  try {
    const response = await fetch(`${API_URL}/restaurants`);
    if (!response.ok) {
      throw new Error("No se pudo obtener la lista de restaurantes");
    }
    restaurants.value = await response.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const createRestaurant = async () => {
  error.value = "";

  try {
    const response = await fetch(`${API_URL}/restaurants`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(form),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.message || "No se pudo crear el restaurante");
    }

    form.name = "";
    form.category = "";
    form.address = "";
    form.rating = 0;

    await fetchRestaurants();
  } catch (err) {
    error.value = err.message;
  }
};

const deleteRestaurant = async (id) => {
  error.value = "";

  try {
    const response = await fetch(`${API_URL}/restaurants/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error("No se pudo eliminar el restaurante");
    }

    await fetchRestaurants();
  } catch (err) {
    error.value = err.message;
  }
};

onMounted(() => {
  fetchRestaurants();
});
</script>

<style>
* {
  box-sizing: border-box;
  font-family: Arial, Helvetica, sans-serif;
}

body {
  margin: 0;
  background: #f5f5f5;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 20px;
}

h1 {
  margin-bottom: 8px;
}

.subtitle {
  margin-top: 0;
  color: #666;
}

.form {
  display: grid;
  gap: 12px;
  margin: 24px 0;
  background: white;
  padding: 20px;
  border-radius: 12px;
}

.form input,
.form button,
.refresh,
.delete {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ccc;
}

.form button,
.refresh,
.delete {
  cursor: pointer;
  border: none;
}

.form button {
  background: #222;
  color: white;
}

.refresh {
  background: #ddd;
  margin-bottom: 20px;
}

.delete {
  background: #d9534f;
  color: white;
  margin-top: 10px;
}

.list {
  display: grid;
  gap: 16px;
}

.card {
  background: white;
  padding: 18px;
  border-radius: 12px;
  box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
}

.error {
  color: #b00020;
  font-weight: bold;
}
</style>