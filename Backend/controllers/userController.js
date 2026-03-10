const createCrudController = require("./crudFactory");
const User = require("../models/User");

module.exports = createCrudController(User);