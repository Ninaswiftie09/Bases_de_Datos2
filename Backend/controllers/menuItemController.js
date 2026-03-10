const createCrudController = require("./crudFactory");
const MenuItem = require("../models/MenuItem");

module.exports = createCrudController(MenuItem);