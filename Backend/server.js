const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const userRoutes = require("./routes/userRoutes");
const restaurantRoutes = require("./routes/restaurantRoutes");
const menuItemRoutes = require("./routes/menuItemRoutes");
const orderRoutes = require("./routes/orderRoutes");
const reviewRoutes = require("./routes/reviewRoutes");

const reportRoutes = require("./routes/reportRoutes");

const app = express();

const PORT = process.env.PORT || 8000;
const MONGO_URI =
  process.env.MONGO_URI ||
  "mongodb://admin:admin123@mongo:27017/?authSource=admin";
const DB_NAME = process.env.DB_NAME || "proyecto01";

const fileRoutes = require("./routes/fileRoutes");

app.use(cors());
app.use(express.json());
app.use("/api/files", fileRoutes);

app.get("/api/health", async (req, res) => {
  res.json({
    ok: true,
    message: "Backend funcionando",
    dbState: mongoose.connection.readyState,
    dbName: DB_NAME,
  });
});

app.use("/api/users", userRoutes);
app.use("/api/restaurants", restaurantRoutes);
app.use("/api/menu-items", menuItemRoutes);
app.use("/api/orders", orderRoutes);
app.use("/api/reviews", reviewRoutes);

app.use("/api/reports", reportRoutes);

app.use((req, res) => {
  res.status(404).json({ message: "Ruta no encontrada" });
});

async function startServer() {
  try {
    await mongoose.connect(MONGO_URI, {
      dbName: DB_NAME,
    });

    console.log(`Conectado a MongoDB en la base ${DB_NAME}`);

    app.listen(PORT, "0.0.0.0", () => {
      console.log(`Servidor corriendo en puerto ${PORT}`);
    });
  } catch (error) {
    console.error("Error conectando a MongoDB:", error.message);
    process.exit(1);
  }
}

startServer();