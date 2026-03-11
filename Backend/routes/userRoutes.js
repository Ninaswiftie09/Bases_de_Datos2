const express = require("express");
const userController = require("../controllers/userController");

const router = express.Router();

router.post("/", userController.createOne);
router.get("/", userController.getAll);
router.get("/:id", userController.getOne);
router.patch("/:id", userController.updateOne);
router.delete("/:id", userController.deleteOne);
router.delete("/:id/address", userController.removeAddress);

router.post("/:id/address", userController.addAddress);

module.exports = router;