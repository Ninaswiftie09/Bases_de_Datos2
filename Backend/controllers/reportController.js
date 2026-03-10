const Order = require("../models/Order");
const Review = require("../models/Review");

exports.topRestaurants = async (req, res) => {
  try {
    const result = await Review.aggregate([
      {
        $group: {
          _id: "$restaurant_id",
          avgRating: { $avg: "$rating" },
          totalReviews: { $sum: 1 }
        }
      },
      { $sort: { avgRating: -1 } },
      { $limit: 5 }
    ]);

    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

exports.topDishes = async (req, res) => {
  try {
    const result = await Order.aggregate([
      { $unwind: "$items" },
      {
        $group: {
          _id: "$items.menu_item_id",
          totalSold: { $sum: "$items.quantity" }
        }
      },
      { $sort: { totalSold: -1 } },
      { $limit: 5 }
    ]);

    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

exports.ordersByStatus = async (req, res) => {
  try {
    const result = await Order.aggregate([
      {
        $group: {
          _id: "$status",
          total: { $sum: 1 }
        }
      }
    ]);

    res.json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

exports.testExplain = async (req, res) => {
  const result = await Order.find({ status: "completed" })
    .explain("executionStats");

  res.json(result);
};