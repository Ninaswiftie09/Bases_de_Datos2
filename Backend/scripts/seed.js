const mongoose = require("mongoose");
require("dotenv").config();

const User = require("../models/User");
const Restaurant = require("../models/Restaurant");
const MenuItem = require("../models/MenuItem");
const Order = require("../models/Order");
const Review = require("../models/Review");

const MONGO_URI =
  process.env.MONGO_URI ||
  "mongodb://admin:admin123@mongo:27017/?authSource=admin";
const DB_NAME = process.env.DB_NAME || "proyecto01";

const firstNames = [
  "Ana",
  "Luis",
  "Carlos",
  "María",
  "Elena",
  "Jorge",
  "Sofía",
  "Lucía",
  "Pedro",
  "Valeria",
  "Camila",
  "Andrés",
  "Daniela",
  "Fernando",
  "Paula",
];

const lastNames = [
  "Pérez",
  "García",
  "López",
  "Ramírez",
  "Méndez",
  "Castillo",
  "Díaz",
  "Rodríguez",
  "Sosa",
  "Morales",
  "Nájera",
  "Marakovits",
];

const categories = [
  "Pizza",
  "Hamburguesas",
  "Sushi",
  "Tacos",
  "Comida china",
  "Café",
  "Postres",
  "Comida típica",
];

const restaurantNames = [
  "La Esquina",
  "Sabor Chapín",
  "Pizza House",
  "Sushi Garden",
  "Burger Point",
  "Taco Route",
  "Coffee Mood",
  "Dulce Vida",
  "Bistro Central",
  "La Parrilla",
  "Casa Noodle",
  "Urban Bites",
];

const streets = [
  "Avenida Las Américas",
  "Boulevard Los Próceres",
  "Zona 10",
  "Zona 14",
  "Zona 15",
  "Carretera a El Salvador",
  "Calzada Roosevelt",
  "Zona 1",
];

const itemNames = [
  "Pizza Pepperoni",
  "Hamburguesa Clásica",
  "Taco al Pastor",
  "Sushi Roll",
  "Café Latte",
  "Brownie",
  "Enchiladas",
  "Chow Mein",
  "Quesadilla",
  "Cheesecake",
  "Pasta Alfredo",
  "Pollo Teriyaki",
];

const reviewComments = [
  "Muy rico",
  "Buen servicio",
  "Volvería a pedir",
  "Excelente atención",
  "Me gustó bastante",
  "Podría mejorar",
  "Todo llegó bien",
  "Muy recomendado",
  "La comida estaba fresca",
  "Buen sabor y precio",
];

function randomFrom(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min, max, decimals = 2) {
  return Number((Math.random() * (max - min) + min).toFixed(decimals));
}

function randomPhone(i) {
  return `5${String(1000000 + i).slice(0, 7)}`;
}

function randomEmail(first, last, i) {
  return `${first}.${last}.${i}@correo.com`
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function buildUsers(amount = 100) {
  const users = [];

  for (let i = 0; i < amount; i++) {
    const first = randomFrom(firstNames);
    const last = randomFrom(lastNames);

    users.push({
      name: { first, last },
      email: randomEmail(first, last, i + 1),
      phone: randomPhone(i + 1),
      addresses: [
        {
          label: "Casa",
          street: `${randomFrom(streets)} ${randomInt(1, 30)}-${randomInt(1, 99)}`,
          city: "Guatemala",
          zone: `Zona ${randomInt(1, 18)}`,
          reference: "Portón negro",
        },
      ],
    });
  }

  return users;
}

function buildRestaurants(amount = 20) {
  const restaurants = [];

  for (let i = 0; i < amount; i++) {
    const lng = Number((-90.60 + Math.random() * 0.18).toFixed(6));
    const lat = Number((14.52 + Math.random() * 0.12).toFixed(6));

    restaurants.push({
      name: `${randomFrom(restaurantNames)} ${i + 1}`,
      category: randomFrom(categories),
      location: {
        address: `${randomFrom(streets)}, Guatemala`,
        geo: {
          type: "Point",
          coordinates: [lng, lat],
        },
      },
      avg_rating: randomFloat(3.5, 5, 1),
      review_count: randomInt(0, 200),
    });
  }

  return restaurants;
}

function buildMenuItems(restaurants) {
  const menuItems = [];

  restaurants.forEach((restaurant) => {
    const amount = 10;

    for (let i = 0; i < amount; i++) {
      menuItems.push({
        restaurant_id: restaurant._id,
        name: `${randomFrom(itemNames)} ${i + 1}`,
        description: "Descripción de prueba del platillo",
        price: randomFloat(15, 120, 2),
        is_available: Math.random() > 0.1,
      });
    }
  });

  return menuItems;
}

function buildOrders(users, restaurants, menuItems, amount = 500) {
  const orders = [];
  const restaurantItemsMap = new Map();

  restaurants.forEach((restaurant) => {
    const items = menuItems.filter(
      (item) => String(item.restaurant_id) === String(restaurant._id)
    );
    restaurantItemsMap.set(String(restaurant._id), items);
  });

  for (let i = 0; i < amount; i++) {
    const user = randomFrom(users);
    const restaurant = randomFrom(restaurants);
    const itemsFromRestaurant =
      restaurantItemsMap.get(String(restaurant._id)) || [];

    const itemsCount = randomInt(1, 4);
    const selectedItems = [];
    let subtotal = 0;

    for (let j = 0; j < itemsCount; j++) {
      const item = randomFrom(itemsFromRestaurant);
      const qty = randomInt(1, 3);

      selectedItems.push({
        menu_item_id: item._id,
        name_snapshot: item.name,
        price_snapshot: item.price,
        qty,
        notes: Math.random() > 0.7 ? "Sin cebolla" : "",
      });

      subtotal += item.price * qty;
    }

    const total = Number(subtotal.toFixed(2));

    orders.push({
      user_id: user._id,
      restaurant_id: restaurant._id,
      status: randomFrom([
        "pending",
        "confirmed",
        "preparing",
        "delivered",
        "cancelled",
      ]),
      items: selectedItems,
      totals: {
        subtotal: total,
        total: total,
      },
    });
  }

  return orders;
}

function buildReviews(users, restaurants, orders, amount = 1000) {
  const reviews = [];

  for (let i = 0; i < amount; i++) {
    const user = randomFrom(users);
    const restaurant = randomFrom(restaurants);
    const useOrder = Math.random() > 0.5;
    const order = useOrder ? randomFrom(orders) : null;

    reviews.push({
      restaurant_id: restaurant._id,
      user_id: user._id,
      order_id: order ? order._id : null,
      rating: randomInt(1, 5),
      comment: randomFrom(reviewComments),
    });
  }

  return reviews;
}

async function seed() {
  try {
    await mongoose.connect(MONGO_URI, { dbName: DB_NAME });
    console.log("Conectado a MongoDB para seed");

    await Promise.all([
      User.deleteMany({}),
      Restaurant.deleteMany({}),
      MenuItem.deleteMany({}),
      Order.deleteMany({}),
      Review.deleteMany({}),
    ]);

    console.log("Colecciones limpiadas");

    const users = await User.insertMany(buildUsers(100));
    console.log(`Users insertados: ${users.length}`);

    const restaurants = await Restaurant.insertMany(buildRestaurants(20));
    console.log(`Restaurants insertados: ${restaurants.length}`);

    const menuItems = await MenuItem.insertMany(buildMenuItems(restaurants));
    console.log(`MenuItems insertados: ${menuItems.length}`);

    const orders = await Order.insertMany(
      buildOrders(users, restaurants, menuItems, 500)
    );
    console.log(`Orders insertadas: ${orders.length}`);

    const reviews = await Review.insertMany(
      buildReviews(users, restaurants, orders, 1000)
    );
    console.log(`Reviews insertadas: ${reviews.length}`);

    console.log("Seed normal completado");
    process.exit(0);
  } catch (error) {
    console.error("Error en seed:", error);
    process.exit(1);
  }
}

seed();