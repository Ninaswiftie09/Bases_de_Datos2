const Order = require("../models/Order");
const QueryFeatures = require("../utils/queryFeatures");

exports.getAllOrders = async (req, res) => {
  try {
    const features = new QueryFeatures(Order.find(), req.query)
      .filter()
      .sort()
      .paginate();

    if (req.query.fields) {
      const fields = req.query.fields.split(",").join(" ");
      features.query = features.query.select(fields);
    }

    const orders = await features.query
      .populate({
        path: "user_id",
        select: "name email"
      })
      .populate({
        path: "restaurant_id",
        select: "name category"
      })
      .populate({
        path: "items.menu_item_id",
        select: "name price"
      });

    res.status(200).json({
      status: "success",
      results: orders.length,
      data: orders
    });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};