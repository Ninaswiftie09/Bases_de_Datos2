const express = require("express");

function createCrudRouter(controller) {
  const router = express.Router();

  router.post("/bulk", controller.createMany);
  router.patch("/bulk/update", controller.updateMany);
  router.delete("/bulk/delete", controller.deleteMany);

  router.post("/", controller.createOne);
  router.get("/", controller.getAll);
  router.get("/:id", controller.getOne);
  router.put("/:id", controller.updateOne);
  router.patch("/:id", controller.updateOne);
  router.delete("/:id", controller.deleteOne);

  return router;
}

module.exports = createCrudRouter;