const createCrudRouter = require("./createCrudRouter");
const userController = require("../controllers/userController");

module.exports = createCrudRouter(userController);