const createCrudController = require("./crudFactory");
const Order = require("../models/Order");
const QueryFeatures = require("../utils/queryFeatures");

const mongoose = require("mongoose");
const User = require("../models/User");
const Restaurant = require("../models/Restaurant");
const MenuItem = require("../models/MenuItem");

const crud = createCrudController(Order);

exports.getAll = crud.getAll;
exports.getOne = crud.getOne;
exports.updateOne = crud.updateOne;
exports.deleteOne = crud.deleteOne;

// CREACIÓN DE ORDENES
// PRIMERO SE VALIDA QUE...

exports.createOrder = async (req, res) => {
  try {
    const { user_id, restaurant_id, items } = req.body;

    // EL USUARIO EXISTA
    const user = await User.findById(user_id);
    if (!user) throw new Error("Usuario no existe");

    // EL RESTAURANTE EXISTA
    const restaurant = await Restaurant.findById(restaurant_id);
    if (!restaurant) throw new Error("Restaurante no existe");

    let subtotal = 0;
    const itemsSnapshot = [];

    for (let item of items) {
      
      // EL EL PRODUCTO EXISTA
      const menuItem = await MenuItem.findById(item.menu_item_id);
      if (!menuItem) throw new Error("Menu item no existe");

      // EL PRODUCTO PERTENEZCA AL RESTAURANTE CORRECTO
      if (menuItem.restaurant_id.toString() !== restaurant_id) {
        throw new Error("Item no pertenece al restaurante");
      }

      // y se calcula el subtotal
      const itemSubtotal = menuItem.price * item.qty;
      subtotal += itemSubtotal;

      // Snapshot del producto para mantener consistencia, por si cambia en el futuro
      // en las ordenes antiguas estará el precio original

      itemsSnapshot.push({
        menu_item_id: menuItem._id,
        name_snapshot: menuItem.name,
        price_snapshot: menuItem.price,
        qty: item.qty,
        notes: item.notes || ""
      });
    }

    // el total final
    const total = subtotal;

    const newOrder = await Order.create({
      user_id,
      restaurant_id,
      items: itemsSnapshot,
      totals: { subtotal, total }
    });

    res.status(201).json({
      status: "success",
      data: newOrder
    });

  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

exports.getAllOrdersAdvanced = async (req, res) => {
  try {
    const features = new QueryFeatures(Order.find(), req.query)
      .filter()
      .sort()
      .paginate();

    const orders = await features.query
      .populate("user_id")
      .populate("restaurant_id")
      .populate("items.menu_item_id");

    res.status(200).json({
      status: "success",
      results: orders.length,
      data: orders
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};