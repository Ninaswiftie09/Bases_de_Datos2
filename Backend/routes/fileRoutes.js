const express = require("express");
const fileController = require("../controllers/fileController");

const router = express.Router();

router.post("/", fileController.upload.single("file"), fileController.uploadFile);
router.get("/", fileController.getFiles);
router.get("/:filename", fileController.downloadFile);
router.delete("/:id", fileController.deleteFile);

module.exports = router;