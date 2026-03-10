const createCrudRouter = require("./createCrudRouter");
const restaurantController = require("../controllers/restaurantController");

module.exports = createCrudRouter(restaurantController);