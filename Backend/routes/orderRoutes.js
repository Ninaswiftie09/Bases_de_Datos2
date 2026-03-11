const express = require("express");
const orderController = require("../controllers/orderController");

const router = express.Router();

router.post("/", orderController.createOrder);
router.get("/", orderController.getAll);
router.get("/:id", orderController.getOne);
router.patch("/:id", orderController.updateOne);
router.delete("/:id", orderController.deleteOne);

module.exports = router;