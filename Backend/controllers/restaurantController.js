const createCrudController = require("./crudFactory");
const Restaurant = require("../models/Restaurant");

module.exports = createCrudController(Restaurant);