const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const Restaurant = require("./models/Restaurant");

const app = express();

const PORT = process.env.PORT || 8000;
const MONGO_URI =
  process.env.MONGO_URI ||
  "mongodb://admin:admin123@mongo:27017/?authSource=admin";
const DB_NAME = process.env.DB_NAME || "proyecto01";

app.use(cors());
app.use(express.json());

mongoose
  .connect(MONGO_URI, {
    dbName: DB_NAME,
  })
  .then(() => {
    console.log(`Conectado a MongoDB, base: ${DB_NAME}`);
  })
  .catch((error) => {
    console.error("Error conectando a MongoDB:", error.message);
  });

app.get("/api/health", (req, res) => {
  res.json({
    ok: true,
    message: "Backend funcionando",
    dbState: mongoose.connection.readyState,
  });
});

app.get("/api/restaurants", async (req, res) => {
  try {
    const restaurants = await Restaurant.find().sort({ createdAt: -1 });
    res.json(restaurants);
  } catch (error) {
    res.status(500).json({ message: "Error al obtener restaurantes" });
  }
});

app.post("/api/restaurants", async (req, res) => {
  try {
    const { name, category, address, rating } = req.body;

    if (!name || !category || !address) {
      return res.status(400).json({
        message: "name, category y address son obligatorios",
      });
    }

    const newRestaurant = new Restaurant({
      name,
      category,
      address,
      rating: rating ?? 0,
    });

    const savedRestaurant = await newRestaurant.save();
    res.status(201).json(savedRestaurant);
  } catch (error) {
    res.status(500).json({ message: "Error al crear restaurante" });
  }
});

app.put("/api/restaurants/:id", async (req, res) => {
  try {
    const updatedRestaurant = await Restaurant.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );

    if (!updatedRestaurant) {
      return res.status(404).json({ message: "Restaurante no encontrado" });
    }

    res.json(updatedRestaurant);
  } catch (error) {
    res.status(500).json({ message: "Error al actualizar restaurante" });
  }
});

app.delete("/api/restaurants/:id", async (req, res) => {
  try {
    const deletedRestaurant = await Restaurant.findByIdAndDelete(req.params.id);

    if (!deletedRestaurant) {
      return res.status(404).json({ message: "Restaurante no encontrado" });
    }

    res.json({ message: "Restaurante eliminado correctamente" });
  } catch (error) {
    res.status(500).json({ message: "Error al eliminar restaurante" });
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Servidor corriendo en puerto ${PORT}`);
});