const createCrudController = require("./crudFactory");
const Order = require("../models/Order");
const QueryFeatures = require("../utils/queryFeatures");

module.exports = createCrudController(Order);


exports.getAllOrdersAdvanced = async (req, res) => {
  try {
    const features = new QueryFeatures(Order.find(), req.query)
      .filter()
      .sort()
      .limitFields()
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