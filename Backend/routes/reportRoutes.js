const express = require("express");
const reportController = require("../controllers/reportController");

const router = express.Router();

router.get("/top-restaurants", reportController.topRestaurants);
router.get("/top-dishes", reportController.topDishes);
router.get("/orders-by-status", reportController.ordersByStatus);
router.get("/explain", reportController.testExplain);

module.exports = router;