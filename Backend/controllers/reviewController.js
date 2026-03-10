const createCrudController = require("./crudFactory");
const Review = require("../models/Review");

module.exports = createCrudController(Review);