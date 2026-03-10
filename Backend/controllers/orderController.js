const createCrudController = require("./crudFactory");
const Order = require("../models/Order");

module.exports = createCrudController(Order);