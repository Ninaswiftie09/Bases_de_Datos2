const createCrudRouter = require("./createCrudRouter");
const menuItemController = require("../controllers/menuItemController");

module.exports = createCrudRouter(menuItemController);