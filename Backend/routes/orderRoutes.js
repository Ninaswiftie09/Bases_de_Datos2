const createCrudRouter = require("./createCrudRouter");
const orderController = require("../controllers/orderController");

module.exports = createCrudRouter(orderController);