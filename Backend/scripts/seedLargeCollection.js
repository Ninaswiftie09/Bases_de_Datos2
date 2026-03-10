const mongoose = require("mongoose");
require("dotenv").config();

const User = require("../models/User");
const Restaurant = require("../models/Restaurant");
const Review = require("../models/Review");

const MONGO_URI =
  process.env.MONGO_URI ||
  "mongodb://admin:admin123@mongo:27017/?authSource=admin";
const DB_NAME = process.env.DB_NAME || "proyecto01";

const comments = [
  "Muy rico",
  "Buen servicio",
  "Entrega rápida",
  "Excelente experiencia",
  "Todo muy bien",
  "Podría mejorar",
  "Muy recomendado",
  "Volvería a pedir",
  "Buen precio",
  "La comida llegó caliente",
];

function randomFrom(array) {
  return array[Math.floor(Math.random() * array.length)];
}

function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function seedLargeCollection() {
  try {
    await mongoose.connect(MONGO_URI, { dbName: DB_NAME });
    console.log("Conectado a MongoDB para seed grande");

    const users = await User.find({}, { _id: 1 }).lean();
    const restaurants = await Restaurant.find({}, { _id: 1 }).lean();

    if (users.length === 0 || restaurants.length === 0) {
      console.log(
        "Primero corré npm run seed para tener users y restaurants base"
      );
      process.exit(1);
    }

    const totalDocs = 50000;
    const batchSize = 5000;
    let inserted = 0;

    for (let offset = 0; offset < totalDocs; offset += batchSize) {
      const batch = [];

      for (let i = 0; i < batchSize; i++) {
        const user = randomFrom(users);
        const restaurant = randomFrom(restaurants);

        batch.push({
          restaurant_id: restaurant._id,
          user_id: user._id,
          order_id: null,
          rating: randomInt(1, 5),
          comment: randomFrom(comments),
          created_at: new Date(),
          updated_at: new Date(),
        });
      }

      await Review.insertMany(batch, { ordered: false });
      inserted += batch.length;
      console.log(`Insertados ${inserted} / ${totalDocs}`);
    }

    console.log("Colección grande creada correctamente en reviews");
    process.exit(0);
  } catch (error) {
    console.error("Error en seedLargeCollection:", error);
    process.exit(1);
  }
}

seedLargeCollection();